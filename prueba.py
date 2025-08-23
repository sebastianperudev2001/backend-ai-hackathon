from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatAnthropic(
    model=os.getenv("CLAUDE_MODEL"),
    temperature=0,
    max_tokens=1024,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

chain = llm 

def main():
    print(chain.invoke("Hola, ¿cómo estás?"))

if __name__ == "__main__":
    main()