import asyncio
import base64

from backend.config import get_config
from backend.tools.base import BaseTool

_browser = None
_page = None


async def _get_page():
    global _browser, _page
    if _page is None:
        from playwright.async_api import async_playwright
        pw = await async_playwright().start()
        config = get_config()
        _browser = await pw.chromium.launch(headless=config.browser_headless)
        context = await _browser.new_context()
        _page = await context.new_page()
    return _page


class OpenUrlTool(BaseTool):
    name = "open_url"
    description = "Navigate the browser to a URL"
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to navigate to"},
        },
        "required": ["url"],
    }

    async def execute(self, url: str) -> str:
        page = await _get_page()
        await page.goto(url, wait_until="domcontentloaded")
        return f"Navigated to {page.url} — Title: {await page.title()}"


class LoginWebsiteTool(BaseTool):
    name = "login_website"
    description = "Log into a website using stored credentials. The site_key must match an entry in credentials.json."
    parameters = {
        "type": "object",
        "properties": {
            "site_key": {"type": "string", "description": "Key in credentials.json (e.g. 'github.com')"},
        },
        "required": ["site_key"],
    }

    async def execute(self, site_key: str) -> str:
        creds = get_config().get_site_credentials(site_key)
        page = await _get_page()

        await page.goto(creds["url"], wait_until="domcontentloaded")
        await page.fill(creds["username_field"], creds["username"])
        await page.fill(creds["password_field"], creds["password"])
        await page.click(creds["submit_button"])
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)

        return f"Logged into {site_key} — now at {page.url}"


class GetPageContentTool(BaseTool):
    name = "get_page_content"
    description = "Extract text content from the current page or a specific element"
    parameters = {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector to extract from (optional, defaults to body)"},
        },
        "required": [],
    }

    async def execute(self, selector: str = "body") -> str:
        page = await _get_page()
        element = await page.query_selector(selector)
        if not element:
            return f"No element found for selector '{selector}'"
        text = await element.inner_text()
        if len(text) > 5000:
            text = text[:5000] + "\n... (truncated)"
        return text


class ClickElementTool(BaseTool):
    name = "click_element"
    description = "Click on a page element matched by CSS selector"
    parameters = {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector of element to click"},
        },
        "required": ["selector"],
    }

    async def execute(self, selector: str) -> str:
        page = await _get_page()
        await page.click(selector)
        await asyncio.sleep(1)
        return f"Clicked '{selector}' — now at {page.url}"


class TypeTextTool(BaseTool):
    name = "type_text"
    description = "Type text into a page input element"
    parameters = {
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector of input element"},
            "text": {"type": "string", "description": "Text to type"},
        },
        "required": ["selector", "text"],
    }

    async def execute(self, selector: str, text: str) -> str:
        page = await _get_page()
        await page.fill(selector, text)
        return f"Typed {len(text)} chars into '{selector}'"


class TakeScreenshotTool(BaseTool):
    name = "take_screenshot"
    description = "Take a screenshot of the current browser page"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def execute(self) -> str:
        page = await _get_page()
        screenshot_bytes = await page.screenshot()
        b64 = base64.b64encode(screenshot_bytes).decode()
        return f"Screenshot taken ({len(screenshot_bytes)} bytes). Base64: {b64[:100]}..."
