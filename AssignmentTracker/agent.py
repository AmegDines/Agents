import json
import os
from typing import Any

from groq import Groq

assignments: list[dict[str, str]] = []
chat_memory: list[dict[str, Any]] = []

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_assignment",
            "description": "Add an assignment and its due date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Assignment or test name"},
                    "due": {"type": "string", "description": "Due date as the user described it"},
                },
                "required": ["name", "due"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_assignment",
            "description": "Remove an assignment by name and optional due date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Assignment or test name to remove"},
                    "due": {
                        "type": "string",
                        "description": "Optional due date to match when removing the assignment",
                    },
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming",
            "description": "Return all saved assignments.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


def add_assignment(name: str, due: str) -> str:
    cleaned_name = (name or "").strip()
    cleaned_due = (due or "").strip()

    if not cleaned_name:
        return json.dumps({"status": "error", "message": "Assignment name is required."})

    assignments.append({"name": cleaned_name, "due": cleaned_due})
    return json.dumps({"status": "added", "assignment": assignments[-1]})


def remove_assignment(name: str, due: str | None = None) -> str:
    cleaned_name = (name or "").strip()
    cleaned_due = (due or "").strip()

    if not cleaned_name:
        return json.dumps({"status": "error", "message": "Assignment name is required."})

    remaining = []
    removed_count = 0

    for item in assignments:
        match = item.get("name", "").strip().casefold() == cleaned_name.casefold()
        if cleaned_due:
            match = match and item.get("due", "").strip().casefold() == cleaned_due.casefold()

        if match:
            removed_count += 1
        else: 
            remaining.append(item)

    assignments[:] = remaining

    if removed_count == 0:
        return json.dumps({"status": "not_found", "name": cleaned_name, "due": cleaned_due})

    return json.dumps(
        {
            "status": "removed",
            "removed_count": removed_count,
            "name": cleaned_name,
            "due": cleaned_due or "any due date",
        }
    )


def get_upcoming() -> str:
    return json.dumps(assignments)


def clear_memory() -> None:
    chat_memory.clear()


def run_agent(user_message: str, model: str | None = None) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add your Groq API key to the environment "
            "before running the agent."
        )

    client = Groq(api_key=api_key)
    model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b") 

    if not chat_memory:
        chat_memory.append(
            {
                "role": "system",
                "content": (
                    "You are an assignment tracker. "
                    "When the user gives an assignment/test/project and a due date, "
                    "use add_assignment. "
                    "When the user asks for saved assignments, use get_upcoming. "
                    "When the user asks to remove an assignment, use remove_assignment. "
                    "After using a tool, answer clearly and briefly. "
                    "Do not invent assignments."
                ),
            }
        )

    chat_memory.append({"role": "user", "content": user_message})

    for _ in range(5):
        response = client.chat.completions.create(
            model=model,
            messages=chat_memory,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        assistant_message = message.model_dump(exclude_none=True)
        chat_memory.append(assistant_message)

        if not message.tool_calls:
            return message.content or "Done."

        for call in message.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                result = "Invalid tool arguments."
            else:
                if name == "add_assignment":
                    result = add_assignment(
                        args.get("name", ""),
                        args.get("due", ""),
                    )
                elif name == "remove_assignment":
                    result = remove_assignment(
                        args.get("name", ""),
                        args.get("due"),
                    )
                elif name == "get_upcoming":
                    result = get_upcoming()
                else:
                    result = f"Unknown tool: {name}"

            chat_memory.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )

    return "The agent reached its tool-call limit."