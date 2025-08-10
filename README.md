## gen-ai-agent

A minimal research assistant powered by LangChain and OpenAI. It answers a user query, optionally calls Wikipedia for context, formats the final answer to a strict schema (Pydantic), and saves the result to a text file.

### Features
- Structured outputs via a Pydantic model (`ResearchResponse`)
- Tool-enabled agent (Wikipedia search)
- Configurable agent loop limits (`max_iterations`) and early-stop behavior
- Saves results to `research-output.txt` (append or overwrite)
- Verbose run logs for easier debugging

### Requirements
- Python 3.12+
- An OpenAI API key (for `ChatOpenAI`)

### Setup
1) Clone and enter the project
2) Create and activate a virtual environment
   - Windows PowerShell:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
3) Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```
4) Configure environment variables
   - Create a `.env` file in the project root with:
     ```env
     OPENAI_API_KEY=your_openai_api_key
     ```

### Run
```powershell
python main.py
```
- You will be prompted: `what can i help you research?` Enter a topic (e.g., "hammerhead shark").
- The terminal will show the agent steps (tool calls, etc.).
- The final structured JSON is returned in-memory and saved to `research-output.txt`.

### How it works
- `main.py`
  - Defines `ResearchResponse` (Pydantic model with fields: `topic`, `summary`, `sources`, `tools_used`).
  - Builds a `PydanticOutputParser` from that model and injects its `get_format_instructions()` into the prompt.
  - Creates a tool-enabled agent (`wikipedia`, `save_text_to_file`).
  - Runs the agent with `AgentExecutor` and caps loops via `max_iterations`.
  - Parses the final JSON string into `ResearchResponse` and saves the output to a file.
- `tools.py`
  - `wiki_tool`: Wikipedia retrieval via `langchain_community`.
  - `save_tool`: wraps `save_to_txt(data: str, filename: str = "research-output.txt", overwrite: bool = False)`
    - Set `overwrite=True` to replace file contents each run.

### Output files
- `research-output.txt`
  - Contains a timestamped header and the text you pass in (either raw JSON or human-readable text you compose from parsed fields).
  - By default appends; pass `overwrite=True` to replace.

### Common tasks
- Save raw JSON string returned by the agent:
  ```python
  save_tool.func(raw_response["output"], filename="research-output.txt")
  ```
- Save validated, pretty JSON (Pydantic v2):
  ```python
  structured = parser.parse(raw_response["output"])  # -> ResearchResponse
  pretty = structured.model_dump_json(indent=2)
  save_tool.func(pretty, filename="research-output.txt", overwrite=True)
  ```
- Save a human-readable report:
  ```python
  text = (
      f"Topic: {structured.topic}\n\n"
      f"Summary:\n{structured.summary}\n\n"
      f"Sources:\n" + "\n".join(structured.sources) + "\n\n"
      f"Tools used:\n" + "\n".join(structured.tools_used) + "\n"
  )
  save_tool.func(text, filename="research-output.txt", overwrite=True)
  ```

### Troubleshooting
- Agent loops on Wikipedia and stops early
  - Increase `doc_content_chars_max` in `tools.py` to fetch more content per call
  - Reduce loops with `max_iterations` and strengthen the prompt (“use at most 1 Wikipedia call”)
  - Use `early_stopping_method="force"` (supported broadly). If you want a synthesized final answer, do a separate follow-up LLM call.
- Output parsing fails
  - Catch exceptions and fall back to saving the raw JSON string
  - Ensure you’re parsing `raw_response["output"]` (a JSON string), not the whole `raw_response` dict
- Virtual environment not used
  - Ensure the prompt shows `(venv)` and `where python` / `where pip` point into `venv/`
- DuckDuckGo rate-limit errors
  - This project currently uses Wikipedia only. If you add DuckDuckGo, add retry/backoff or use an alternative provider

### Git hygiene
- Generated files: add to `.gitignore`
  - `research-output.txt` or `research-output*.txt`
  - `__pycache__/`, `*.pyc`, `venv/`
- Update dependencies when they change:
  ```powershell
  pip freeze > requirements.txt
  git add requirements.txt
  git commit -m "Pin dependencies"
  git push
  ```

### Notes
- The LLM’s final JSON is a string in `raw_response["output"]`. Parse with `parser.parse(...)` to get a validated model; serialize with `model_dump_json()` for pretty JSON, or build a readable text report.
- Verbose logs (`verbose=True`) print chain/tool steps; set `verbose=False` for a quieter run.