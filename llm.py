"""LLM factory. Swap providers with LLM_PROVIDER in .env, no other code changes."""
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODELS = {
    "gemini": "gemini-3.8-flash",
    "groq": "llama-3.3-70b-versatile",
    "ollama": "llama3.1",
}


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model = os.getenv("LLM_MODEL", DEFAULT_MODELS[provider])

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model, temperature=0)  # uses GOOGLE_API_KEY
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, temperature=0)  # uses GROQ_API_KEY
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, temperature=0)
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def text_of(message) -> str:
    """Some providers return content as a list of blocks; normalise to str."""
    c = message.content
    if isinstance(c, str):
        return c
    return "".join(b.get("text", "") for b in c if isinstance(b, dict))
