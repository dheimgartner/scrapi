import time

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

# TODO: look into Iframe and Shadow DOM cookies


class SeleniumHTMLDownloader:
    """Download webpage HTML content using Selenium and Microsoft Edge.

    This class loads webpages in a browser instance and returns the
    rendered HTML source. Before extracting the page content, it attempts
    to automatically dismiss common cookie consent dialogs by clicking
    buttons whose text matches a predefined set of acceptance keywords.

    The browser can be run either in headless mode or as a visible window
    for debugging purposes.

    Attributes:
        ACCEPT_KEYWORDS (list[str]): Keywords used to identify cookie
            consent acceptance buttons in multiple languages.

    """

    ACCEPT_KEYWORDS = [
        # English
        "accept",
        "agree",
        "allow",
        "consent",
        "ok",
        "got it",
        # German
        "akzeptieren",
        "zustimmen",
        "einverstanden",
        # French
        "accepter",
        "j'accepte",
        "d'accord",
        # Italian
        "accetta",
        "accettare",
        "accetto",
        "consenti",
    ]

    def __init__(self, page_load_timeout: int = 15, browser_visibility: bool = False):
        """Initialize the Selenium downloader.

        Args:
            page_load_timeout (int): Maximum number of seconds to wait for a
                page to load.
            browser_visibility (bool): Whether to display the browser window.
                If ``False``, the browser runs in headless mode.

        """
        options = Options()
        if not browser_visibility:
            options.add_argument("--headless=new")

        self._driver = webdriver.Edge(options=options)
        self._driver.set_page_load_timeout(page_load_timeout)

    def download_html(self, url: str) -> str:
        """Download the rendered HTML content of a webpage.

        The page is loaded in the browser and common cookie consent dialogs
        are automatically accepted when possible. The rendered page source is
        then returned.

        Args:
            url (str): URL of the webpage to download.

        Returns:
            str: The rendered HTML content of the page.

        """
        self._driver.get(url)
        time.sleep(4)

        buttons = self._driver.find_elements(By.TAG_NAME, "button")
        accept_buttons = []

        for btn in buttons:
            text = btn.text.lower() if btn.text else ""

            if any(keyword in text for keyword in self.ACCEPT_KEYWORDS):
                accept_buttons.append(btn)

        if accept_buttons:
            accept_buttons[0].click()

        return self._driver.page_source
