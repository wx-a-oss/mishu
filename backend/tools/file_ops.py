import os
from pathlib import Path

from backend.config import get_config
from backend.tools.base import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file at the given path"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to read"},
        },
        "required": ["path"],
    }

    async def execute(self, path: str) -> str:
        resolved = get_config().validate_path(path)
        return resolved.read_text(encoding="utf-8")


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Create or overwrite a file with the given content"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to write to"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    }

    async def execute(self, path: str, content: str) -> str:
        resolved = get_config().validate_path(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return f"Written {len(content)} chars to {resolved}"


class UpdateFileTool(BaseTool):
    name = "update_file"
    description = "Find and replace text in a file"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to update"},
            "old_text": {"type": "string", "description": "Text to find"},
            "new_text": {"type": "string", "description": "Replacement text"},
        },
        "required": ["path", "old_text", "new_text"],
    }

    async def execute(self, path: str, old_text: str, new_text: str) -> str:
        resolved = get_config().validate_path(path)
        content = resolved.read_text(encoding="utf-8")
        if old_text not in content:
            return f"Error: '{old_text}' not found in {resolved}"
        updated = content.replace(old_text, new_text)
        resolved.write_text(updated, encoding="utf-8")
        count = content.count(old_text)
        return f"Replaced {count} occurrence(s) in {resolved}"


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Delete a file at the given path"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path to delete"},
        },
        "required": ["path"],
    }

    async def execute(self, path: str) -> str:
        resolved = get_config().validate_path(path)
        if not resolved.exists():
            return f"Error: {resolved} does not exist"
        resolved.unlink()
        return f"Deleted {resolved}"


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List files and directories at the given path"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path to list"},
        },
        "required": ["path"],
    }

    async def execute(self, path: str) -> str:
        resolved = get_config().validate_path(path)
        if not resolved.is_dir():
            return f"Error: {resolved} is not a directory"
        entries = []
        for entry in sorted(resolved.iterdir()):
            kind = "dir" if entry.is_dir() else "file"
            size = entry.stat().st_size if entry.is_file() else ""
            entries.append(f"[{kind}] {entry.name}" + (f" ({size} bytes)" if size else ""))
        return "\n".join(entries) if entries else "(empty directory)"


class CreateDirectoryTool(BaseTool):
    name = "create_directory"
    description = "Create a directory (including parent directories)"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path to create"},
        },
        "required": ["path"],
    }

    async def execute(self, path: str) -> str:
        resolved = get_config().validate_path(path)
        resolved.mkdir(parents=True, exist_ok=True)
        return f"Created directory {resolved}"
