import functools
import os
from pathlib import Path
import psutil
import subprocess
import sys
from threading import Lock
import time
import types
from typing import Self, Type, Callable, Any

import truststore


class _ProxySession:
    """Manage the lifecycle of a local Px proxy process.

    This class provides reference-counted access to a shared Px proxy
    instance. The proxy process is started when the first consumer acquires
    the session and terminated when the last consumer releases it.

    The class is intended to be used as a singleton through the module-level
    'PROXY_SESSION' instance. Creating additional instances is not
    supported and may result in multiple independently managed proxy
    processes.

    The session can be used either through the ``acquire()`` and
    ``release()`` methods or as a context manager.

    Attributes:
        counter (int): Number of active consumers currently using the proxy.
        proxy_url (str): URL of the local Px proxy endpoint.
        root_ca_path (str): Path to the trusted CA bundle.

    """

    def __init__(self) -> None:
        self.counter = 0
        self.proxy_url = "http://127.0.0.1:3128"
        self.root_ca_path = self._get_root_ca_path()

        self._lock = Lock()
        self._px_proc = None

        os.environ["HTTP_PROXY"] = self.proxy_url
        os.environ["HTTPS_PROXY"] = self.proxy_url
        truststore.inject_into_ssl()

    def __enter__(self) -> Self:
        self.acquire()

        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.release()

    def with_proxy_session(self, func: Callable) -> Callable:
        """Decorator that wraps a callable in the proxy session context."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with self:
                return func(*args, **kwargs)

        return wrapper

    def acquire(self) -> None:
        with self._lock:
            if self.counter == 0:
                self._start_proxy()

            self.counter += 1

    def release(self) -> None:
        with self._lock:
            if self.counter <= 0:
                raise "Error"

            self.counter -= 1

            if self.counter == 0:
                self._terminate_proxy()

    @staticmethod
    def _get_root_ca_path() -> str:
        return str(Path(__file__).resolve().parent / "swisscom_finma_ca_bundle.pem")

    def _start_proxy(self) -> None:
        self._px_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "px",
            ]
        )
        print("px proxy started")
        time.sleep(3)

    def _terminate_proxy(self) -> None:
        print("terminating px proxy...")
        parent = psutil.Process(self._px_proc.pid)
        children = parent.children(recursive=True)

        for child in children:
            child.terminate()

        parent.terminate()
        gone, alive = psutil.wait_procs(children + [parent], timeout=5)

        for p in alive:
            p.kill()

        psutil.wait_procs(alive, timeout=5)
        print("px proxy and all child processes terminated.")

PROXY_SESSION = _ProxySession()
