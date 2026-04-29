from backend.tools.base import BaseTool

_tools: dict[str, BaseTool] = {}
_initialized = False


def _register_defaults():
    global _initialized
    if _initialized:
        return
    _initialized = True

    from backend.tools.file_ops import (
        ReadFileTool, WriteFileTool, UpdateFileTool,
        DeleteFileTool, ListDirectoryTool, CreateDirectoryTool,
    )
    from backend.tools.browser import (
        OpenUrlTool, LoginWebsiteTool, GetPageContentTool,
        ClickElementTool, TypeTextTool, TakeScreenshotTool,
    )
    from backend.tools.desktop import (
        MouseClickTool, MouseMoveTool, TypeKeyboardTool,
        PressHotkeyTool, TakeDesktopScreenshotTool,
    )

    for tool_class in [
        ReadFileTool, WriteFileTool, UpdateFileTool,
        DeleteFileTool, ListDirectoryTool, CreateDirectoryTool,
        OpenUrlTool, LoginWebsiteTool, GetPageContentTool,
        ClickElementTool, TypeTextTool, TakeScreenshotTool,
        MouseClickTool, MouseMoveTool, TypeKeyboardTool,
        PressHotkeyTool, TakeDesktopScreenshotTool,
    ]:
        instance = tool_class()
        _tools[instance.name] = instance


def get_all_tools() -> list[BaseTool]:
    _register_defaults()
    return list(_tools.values())


def get_tool_schemas() -> list[dict]:
    return [tool.get_schema() for tool in get_all_tools()]


async def execute_tool(name: str, args: dict) -> str:
    _register_defaults()
    if name not in _tools:
        return f"Error: Unknown tool '{name}'. Available: {list(_tools.keys())}"
    try:
        return await _tools[name].execute(**args)
    except Exception as e:
        return f"Error executing {name}: {type(e).__name__}: {e}"
