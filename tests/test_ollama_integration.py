"""Integration tests for OllamaLLM — require a live Ollama server."""

import socket

import pytest

from scrapi.llm.ollama import OllamaLLM

OLLAMA_HOST = "10.89.0.7"
OLLAMA_PORT = 11434
OLLAMA_BASE_URL = f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/v1"
OLLAMA_MODEL = "gemma3:4b"


def _server_reachable() -> bool:
    try:
        with socket.create_connection((OLLAMA_HOST, OLLAMA_PORT), timeout=2):
            return True
    except OSError:
        return False


requires_ollama = pytest.mark.skipif(
    not _server_reachable(),
    reason=f"Ollama server not reachable at {OLLAMA_HOST}:{OLLAMA_PORT}",
)


@requires_ollama
def test_ollama_llm_init():
    llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    assert llm.llm is not None
    assert llm.meta["model"] == OLLAMA_MODEL
    assert llm.meta["base_url"] == OLLAMA_BASE_URL


@requires_ollama
def test_ollama_llm_prompt():
    llm = OllamaLLM(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    response = llm.prompt("Reply with the single word: hello")
    assert response.content
    assert len(llm.history) == 2  # HumanMessage + AIMessage
