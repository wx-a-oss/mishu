import asyncio
import base64
import io

from backend.tools.base import BaseTool


def _setup_pyautogui():
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.3
    return pyautogui


class MouseClickTool(BaseTool):
    name = "mouse_click"
    description = "Click the mouse at the given screen coordinates"
    parameters = {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "X coordinate"},
            "y": {"type": "integer", "description": "Y coordinate"},
            "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button (default: left)"},
        },
        "required": ["x", "y"],
    }

    async def execute(self, x: int, y: int, button: str = "left") -> str:
        pag = _setup_pyautogui()
        await asyncio.to_thread(pag.click, x, y, button=button)
        return f"Clicked {button} at ({x}, {y})"


class MouseMoveTool(BaseTool):
    name = "mouse_move"
    description = "Move the mouse to the given screen coordinates"
    parameters = {
        "type": "object",
        "properties": {
            "x": {"type": "integer", "description": "X coordinate"},
            "y": {"type": "integer", "description": "Y coordinate"},
        },
        "required": ["x", "y"],
    }

    async def execute(self, x: int, y: int) -> str:
        pag = _setup_pyautogui()
        await asyncio.to_thread(pag.moveTo, x, y)
        return f"Moved mouse to ({x}, {y})"


class TypeKeyboardTool(BaseTool):
    name = "type_keyboard"
    description = "Type text using the keyboard"
    parameters = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to type"},
        },
        "required": ["text"],
    }

    async def execute(self, text: str) -> str:
        pag = _setup_pyautogui()
        await asyncio.to_thread(pag.write, text, interval=0.02)
        return f"Typed {len(text)} characters"


class PressHotkeyTool(BaseTool):
    name = "press_hotkey"
    description = "Press a keyboard shortcut (e.g. 'command+c', 'ctrl+alt+delete')"
    parameters = {
        "type": "object",
        "properties": {
            "keys": {"type": "string", "description": "Key combination separated by '+' (e.g. 'command+c')"},
        },
        "required": ["keys"],
    }

    async def execute(self, keys: str) -> str:
        pag = _setup_pyautogui()
        key_list = [k.strip() for k in keys.split("+")]
        await asyncio.to_thread(pag.hotkey, *key_list)
        return f"Pressed {keys}"


class TakeDesktopScreenshotTool(BaseTool):
    name = "take_desktop_screenshot"
    description = "Take a screenshot of the entire screen"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def execute(self) -> str:
        pag = _setup_pyautogui()
        img = await asyncio.to_thread(pag.screenshot)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        screenshot_bytes = buf.getvalue()
        b64 = base64.b64encode(screenshot_bytes).decode()
        return f"Desktop screenshot taken ({len(screenshot_bytes)} bytes). Base64: {b64[:100]}..."
