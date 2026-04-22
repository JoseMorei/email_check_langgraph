# email_check_langgraph
Email processing system based on LangGraph

![email_check_langgraph workflow](graph.png)

## Workflow

1) Read incoming emails
2) Classify them as spam or legitimate
3) Draft a preliminary response for legitimate emails
4) Send email information when legitimate (printing only)


## Installation

# Install the required packages
pip install -q langgraph langchain_openai langchain_huggingface pyppeteer

## Full Stack

| Tool | Version | Role |
|---|---|---|
| **Python** | 3.14.3 | Runtime |
| **LangGraph** | 1.1.9 | Agent graph orchestration |
| **LangChain Core** | 1.3.0 | LLM abstraction layer |
| **LangChain Ollama** | 1.1.0 | Ollama integration for LangChain |
| **Ollama** | 0.17.2 | Local LLM server |
| **Qwen2 7B** | — | LLM model (via Ollama) |
| **mermaid.ink** | — | Graph diagram rendering (web API) |
| **requests** | 2.33.1 | HTTP client (used to call mermaid.ink) |
| **uv** | — | Python package manager / venv |