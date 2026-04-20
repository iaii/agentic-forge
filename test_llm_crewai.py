from crewai import Agent, LLM
try:
    print("Testing LLM class from crewai...")
    llm = LLM(model="openai/local-model", base_url="http://localhost:1234/v1", api_key="lm-studio")
    print("Success. Instantiating Agent...")
    agent = Agent(role="test", goal="test", backstory="test", llm=llm)
    print("Agent success!")
except ImportError:
    print("No LLM in crewai")
except Exception as e:
    print("Error:", e)
