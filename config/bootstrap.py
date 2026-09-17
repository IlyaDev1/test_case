from pathlib import Path


def load_runtime_env() -> None:
    from dotenv import load_dotenv

    root = Path(__file__).resolve().parents[1]
    try:
        load_dotenv(root / ".env", override=True)
    except PermissionError:
        pass
