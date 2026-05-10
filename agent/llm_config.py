from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

LLM_BACKENDS = {
    "gemini": ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", api_key=GEMINI_API_KEY),
    "ollama": ChatOllama(model="llama3.2:1b"),
}

def get_llm(backend: str):
    try:
        return LLM_BACKENDS[backend]
    except KeyError:
        raise ValueError(f"Unsupported backend {backend}")