import os
from dotenv import load_dotenv
from crewai import LLM

# Load environment variables from .env file
load_dotenv()

def get_llm():
    """
    Returns an instance of crewai.LLM configured via environment variables.
    Defaults point to local LM Studio if OPENAI_API_BASE is set to localhost:1234.
    """
    api_key = os.getenv("OPENAI_API_KEY", "lm-studio")
    base_url = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
    model_name = os.getenv("OPENAI_MODEL_NAME", "local-model")

    # LiteLLM needs the provider prefix (e.g., openai/ prefix forces OpenAI-compatible routing)
    if not model_name.startswith("openai/"):
        model_name = "openai/" + model_name

    return LLM(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        temperature=0.7,
        max_tokens=1500
    )
