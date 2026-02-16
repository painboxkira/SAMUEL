import os
from pathlib import Path

from google import genai


class Gaggle:
    def __init__(self, api_key: str | None = None):
        if api_key is None:
            api_key = self._load_api_key()
        if not api_key:
            raise ValueError("Missing Gemini API key in .env (GEMINI_API_KEY or GOOGLE_API_KEY)")
        self.client = genai.Client(api_key=api_key)

    @staticmethod
    def _load_api_key() -> str | None:
        env_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if env_api_key:
            return env_api_key

        env_path = Path(__file__).resolve().parents[1] / ".env"
        if not env_path.exists():
            return None

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in {"GEMINI_API_KEY", "GOOGLE_API_KEY"} and value:
                return value
        return None

    def generate_response(self, prompt: str, language: str) -> str:
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        system_instruction = (
            "You are a code generation engine. Return only raw code as plain text. "
            "Do not use markdown. Do not use code fences. Do not add explanations, "
            f"labels, or surrounding text. Output only valid {language} code."
        )
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config={"system_instruction": system_instruction},
        )
        text = getattr(response, "text", None)
        if text is None:
            return ""
        return text