SYSTEM_PROMPT = """You are Mishu, an AI assistant that can control the user's computer. You have access to tools for:

1. **File operations**: Read, write, update, and delete files. List and create directories.
2. **Browser automation**: Open URLs, log into websites with stored credentials, extract page content, click elements, type text, take screenshots.
3. **Desktop automation**: Move/click the mouse at screen coordinates, type on the keyboard, press hotkeys, take desktop screenshots.

## Guidelines
- Always confirm what you're about to do before taking destructive actions (deleting files, overwriting content).
- For browser login, use the `login_website` tool with the site key from credentials.json.
- File paths must be within the user's allowed directories.
- When you need to see the screen, take a screenshot first to understand the current state.
- Be concise in your responses. Report what you did and the result.
- If a tool returns an error, explain what went wrong and suggest a fix.
"""


class Conversation:
    def __init__(self, max_messages: int = 50):
        self.messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.max_messages = max_messages

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def add_assistant_tool_calls(self, tool_calls: list[dict]):
        self.messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls})

    def add_tool_result(self, tool_call_id: str, content: str):
        self.messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})

    def get_messages(self) -> list[dict]:
        return self.messages

    def _trim(self):
        if len(self.messages) <= self.max_messages + 1:
            return
        system = self.messages[0]
        keep = self.messages[-(self.max_messages):]
        self.messages = [system] + keep
