# agent/llm_openai.py

import json
import os
from typing import Optional, Any, Type, TYPE_CHECKING

from openai import OpenAI
if TYPE_CHECKING:
    from pydantic import BaseModel

from agent.llm_client import ModelResponse, ToolCall


class OpenAICompatibleLLMClient:
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0,
    ):
        self.model = model or os.environ.get("OPENAI_MODEL")

        if not self.model:
            raise ValueError("Missing model. Set OPENAI_MODEL or pass model=...")

        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        base_url = base_url or os.environ.get("OPENAI_BASE_URL")

        if not api_key:
            raise ValueError("Missing API key. Set OPENAI_API_KEY.")

        client_kwargs = {"api_key": api_key}

        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.temperature = temperature

    def chat(self, messages: list[dict], tools: list[dict]) -> ModelResponse:
        openai_messages = self._convert_messages(messages)
        openai_tools = self._convert_tools(tools)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            tools=openai_tools,
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=self.temperature,
            timeout=None
        )

        message = response.choices[0].message
        print(str(message))
        reasoning_content = getattr(message, "reasoning_content", None)

        if message.tool_calls:
            tool_call = message.tool_calls[0]

            try:
                tool_input = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError as e:
                return ModelResponse(
                    text=f"Model produced invalid tool arguments JSON: {e}"
                )

            return ModelResponse(
                tool_call=ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    input=tool_input,
                ),
                reasoning_content=reasoning_content
            )

        return ModelResponse(
            text=message.content or str(message) or "",
            reasoning_content=reasoning_content,
        )
    
    def chat_structured(
        self,
        messages: list[dict],
        response_model: "Type[BaseModel]"
    ) -> ModelResponse:
        
        openai_messages = self._convert_messages(messages)
        
        def messages_to_str(m):
            return json.dumps(m)
        
        request_messages = [{
            "role": "system",
            "content": (
                "You are a summarization agent. "
                "Read provided messages and figure out if model responded successfully and then provide a summary."
            )
        },
        {
            "role": "user",
            "content": messages_to_str(openai_messages)
        }]
        
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=request_messages,
            response_format=response_model,
            temperature=self.temperature
        )
        
        message = completion.choices[0].message
        print(str(message))
        
        if message.refusal:
            raise ValueError(
                f"Model refused to produce structured output"
            )
            
        parsed = message.parsed
        raw_text = message.content = ""
        
        return ModelResponse(text=raw_text, parsed=parsed)

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """
        Convert internal tool schemas:

            {
              "name": "...",
              "description": "...",
              "input_schema": {...}
            }

        into OpenAI-compatible tool schemas:

            {
              "type": "function",
              "function": {
                "name": "...",
                "description": "...",
                "parameters": {...}
              }
            }
        """

        converted = []

        for tool in tools:
            converted.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            })

        return converted

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """
        Convert our internal context messages into OpenAI-compatible chat messages.

        Internal:
            {"role": "event", "content": {"type": "...", "data": {...}}}

        OpenAI-compatible:
            system/user/assistant/tool
        """

        converted: list[dict[str, Any]] = []

        for message in messages:
            role = message["role"]
            content = message["content"]

            if role in {"system", "user", "assistant"}:
                converted.append({
                    "role": role,
                    "content": content,
                })
                continue

            if role != "event":
                continue

            event_type = content.get("type")
            data = content.get("data", {})

            if event_type == "user_message":
                # Already represented by the original user message.
                continue

            if event_type == "model_tool_call":
                tool_call_id = data.get("id") or "missing_tool_call_id"

                converted.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": data["name"],
                                "arguments": json.dumps(data.get("input", {})),
                            },
                        }
                    ],
                })
                continue

            if event_type == "tool_result":
                tool_call_id = data.get("tool_call_id") or "missing_tool_call_id"

                converted.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(data.get("result", {}), ensure_ascii=False),
                })
                continue

            if event_type == "permission_decision":
                converted.append({
                    "role": "user",
                    "content": (
                        "Permission decision:\n"
                        + json.dumps(data, indent=2, ensure_ascii=False)
                    ),
                })
                continue

        return converted