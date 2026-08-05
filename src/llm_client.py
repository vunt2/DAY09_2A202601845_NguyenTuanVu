import os
import json
import urllib.request
from src.config import OPENROUTER_API_KEY, MODEL_NAME

class LLMClient:
    """
    Client for invoking OpenRouter API with model <= 10B parameters.
    Fallback to Native Engine if no valid API key is set.
    """

    @staticmethod
    def is_api_key_set() -> bool:
        key = OPENROUTER_API_KEY.strip()
        return bool(key and key != "your_openrouter_api_key_here" and not key.startswith("your_"))

    @staticmethod
    def call_openrouter(prompt: str, system_prompt: str = "You are an E-commerce Dispute Resolution AI Agent.") -> dict:
        if not LLMClient.is_api_key_set():
            return {"status": "offline", "reason": "No valid OPENROUTER_API_KEY in .env"}

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/VinUni-AI20k/K3-Day9-Multi-Agent-A2A",
            "X-Title": "K3 Day 9 Multi-Agent"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                response_data = json.loads(resp.read().decode("utf-8"))
                content = response_data["choices"][0]["message"]["content"]
                return {
                    "status": "success",
                    "content": content,
                    "model": response_data.get("model", MODEL_NAME),
                    "usage": response_data.get("usage", {})
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
