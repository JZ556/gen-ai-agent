from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime


def save_to_txt(data:str, filename:str = "research-output.txt", overwrite:bool = False):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    formatted_text = f"---research-output---\n Timestamp: {timestamp}\n\n{data}\n"

    mode = "w" if overwrite else "a"
    with open(filename, mode , encoding="utf-8") as file:
        file.write(formatted_text)

    msg = f"file successfully saved to {filename}"
    print(msg)
    return msg

save_tool = Tool(
    name="save_text_to_file",
    func= save_to_txt,
    description="Save structured research output to a text file",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)