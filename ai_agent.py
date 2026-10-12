import json
import os
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from fastmcp import Client

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8001/mcp")

if not GROQ_API_KEY:
    # Defer raising until a chat request so the API can still start.
    groq_client = None
else:
    groq_client = Groq(api_key=GROQ_API_KEY)


def _jsonable(value: Any):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "__dict__"):
        return value.__dict__
    return value


def _tool_result_text(result: Any) -> str:
    """Convert FastMCP results into text that can be sent back to Groq."""
    result = _jsonable(result)
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False, default=str)
    if isinstance(result, list):
        pieces = []
        for item in result:
            item = _jsonable(item)
            if isinstance(item, dict) and "text" in item:
                pieces.append(str(item["text"]))
            else:
                pieces.append(str(item))
        return "\n".join(pieces)
    return str(result)


async def ask_agent(question: str) -> dict:
    if groq_client is None:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to the .env file and restart the API."
        )

    async with Client(MCP_SERVER_URL) as client:
        mcp_tools = await client.list_tools()

        groq_tools = []
        for tool in mcp_tools:
            schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None)
            if not schema:
                schema = {"type": "object", "properties": {}}
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": getattr(tool, "description", "") or "",
                    "parameters": schema,
                },
            })

        messages = [
            {
                "role": "system",
                "content": (
                    "You are Dev Clinic's AI assistant. Use MCP tools when the user asks "
                    "for doctor or patient records. Never invent database information. "
                    "Only share patient information when specifically requested by patient ID. "
                    "Explain results clearly and concisely. You are not a substitute for "
                    "professional medical advice."
                ),
            },
            {"role": "user", "content": question},
        ]

        first = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=groq_tools if groq_tools else None,
            tool_choice="auto" if groq_tools else "none",
        )

        assistant_message = first.choices[0].message
        tool_calls = assistant_message.tool_calls or []
        if not tool_calls:
            return {
                "answer": assistant_message.content or "I couldn't generate a response.",
                "tools_used": [],
            }

        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in tool_calls
            ],
        })

        tools_used = []
        for call in tool_calls:
            tool_name = call.function.name
            try:
                arguments = json.loads(call.function.arguments or "{}")
                result = await client.call_tool(tool_name, arguments)
                result_text = _tool_result_text(result)
            except Exception as exc:
                result_text = json.dumps({
                    "success": False,
                    "error": f"Tool {tool_name} failed: {type(exc).__name__}: {exc}"
                })

            tools_used.append(tool_name)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result_text,
            })

        final = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tool_choice="none",
        )

        return {
            "answer": final.choices[0].message.content or "I couldn't generate a response.",
            "tools_used": tools_used,
        }
