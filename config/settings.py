import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeepSeekSettings:
    api_key: str
    base_url: str
    model: str
    timeout_sec: float

    @classmethod
    def from_env(cls) -> "DeepSeekSettings":
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set")

        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip(
            "/"
        )
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        timeout_sec = float(os.getenv("DEEPSEEK_TIMEOUT_SEC", "120"))
        return cls(
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_sec=timeout_sec,
        )
