# Bunny Hunter

Bunny Hunter is a small collection of Python tools and agents that work together to search second‑hand markets and find good deals.

## Project layout

- `00-main-agent` – LangGraph based orchestrator.  It uses OpenAI models to search listings, estimate a reasonable price and compose an inquiry.  Helper containers are invoked via Docker.
- `01-search-list` – scraper that queries [당근마켓](https://www.daangn.com/) for past or current listings.  Results are written as JSON to stdout.  It expects environment variables such as `ITEM_NAME`, `MODE` (`ALL` or `CURRENT`) and an optional `REGION`.
- `02-gpt-oss-20b-ollama` – forwards a prompt to an Ollama instance running the `gpt-oss:20b` model.  The prompt is supplied via the `PROMPT` environment variable and the response is emitted as JSON.

## JSON Formatting Features

Bunny Hunter provides exceptionally clean JSON output through sophisticated formatting and parsing capabilities:

### Key Features
- **Korean character preservation** with `ensure_ascii=False`
- **Robust JSON extraction** from mixed logs and output  
- **Safe parsing** with comprehensive error handling
- **Consistent response structure** across all components
- **Real-time output** with `flush=True`

### Usage Examples
```python
# Using the centralized JSON utilities
from json_utils import format_json_clean, extract_json_from_mixed_output

# Clean formatting with Korean support
clean_json = format_json_clean({"메시지": "안녕하세요"}, for_development=True)

# Extract JSON from mixed container output
parsed_data = extract_json_from_mixed_output(container_stdout)
```

See [`JSON_FORMATTING_GUIDE.md`](JSON_FORMATTING_GUIDE.md) for detailed documentation and [`json_utils.py`](00-main-agent/json_utils.py) for the centralized utility functions.

## Requirements

- Python 3.10+ (repository tested with Python 3.12)
- Docker for running the helper containers
- An OpenAI API key available as `OPENAI_API_KEY` or in a `.env` file for the main agent

Install dependencies for the main agent with:

```bash
pip install -r 00-main-agent/requirements.txt
```

## Running

1. Build the helper containers:

```bash
docker build -t search-list 01-search-list
docker build -t gpt-oss-20b-ollama 02-gpt-oss-20b-ollama
```

2. Run the agent:

```bash
cd 00-main-agent
python app.py "아이폰 14 프로"
```

The agent will look up past transactions, estimate a reasonable price and poll for matching deals.  A suggested inquiry message is printed when a candidate is found.

## License

No license file is provided.

