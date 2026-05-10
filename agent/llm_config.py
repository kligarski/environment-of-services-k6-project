import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

load_dotenv()

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
DEFAULT_OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")


def get_backend_order(preferred_backend: str | None = None) -> list[str]:
    backend = (preferred_backend or os.getenv("LLM_BACKEND") or "gemini").lower()

    if backend == "gemini":
        return ["gemini", "ollama"]
    if backend == "ollama":
        return ["ollama", "gemini"]
    if backend == "auto":
        return ["gemini", "ollama"]

    raise ValueError(f"Unsupported backend {backend}")


def get_llm(backend: str):
    backend = backend.lower()

    if backend == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set for Gemini backend")

        return ChatGoogleGenerativeAI(
            model=DEFAULT_GEMINI_MODEL,
            api_key=api_key,
        )

    if backend == "ollama":
        kwargs = {"model": DEFAULT_OLLAMA_MODEL}
        if DEFAULT_OLLAMA_BASE_URL:
            kwargs["base_url"] = DEFAULT_OLLAMA_BASE_URL
        return ChatOllama(**kwargs)

    raise ValueError(f"Unsupported backend {backend}")