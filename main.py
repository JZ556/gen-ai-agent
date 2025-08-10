from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import wiki_tool, save_tool


load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

llm = ChatOpenAI(model="gpt-4o-mini")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         """
         You are a research assistant that will help to generate a research paper.
         Answer the user query and use neccessary tools.
         Wrap the output in this format and provide no other text.\n{format_instructions},
         """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())


tools =[ wiki_tool, save_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools= tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=3, early_stopping_method="force")
query = input("what can i help you research?")
raw_response = agent_executor.invoke({"query": query})
print(raw_response)



try:
    structured_response = parser.parse(raw_response["output"])
    text = f"Topic:{structured_response.topic}\nSummary:{structured_response.summary}\nSources:{structured_response.sources}\nTools Used:{structured_response.tools_used}"
    print(text)
    save_tool.func(text, filename = "research-output.txt")
except Exception as e:
    print(f"Error parsing response: {e}")

