# Multi-Agent Research Assistant

A research pipeline that splits a broad research question across specialized agents — 
search, summarize, and fact-check — coordinated by an orchestrator, producing a more 
reliable report than a single LLM call.

## Core Idea

Orchestrator breaks the research question into sub-tasks → dispatches to specialized 
agents → agents pass structured outputs to each other → orchestrator compiles a final 
report with verified claims and sources.

## How It Works

1. **Query decomposition** — orchestrator breaks a broad question into searchable sub-questions
2. **Search agent** — runs web searches per sub-question, collects and ranks sources
3. **Summarizer agent** — reads sources, extracts key points per sub-question, avoids redundancy
4. **Fact-checker agent** — cross-references summarized claims against original sources, flags unsupported/contradicted claims
5. **Orchestrator compilation** — merges verified summaries into a coherent report with citations
6. **Iteration (optional, capped)** — if fact-checker flags issues, orchestrator sends those sub-questions back to the search agent for more sources, up to `max_iterations`

## 🔄 Data Flow

```text
User Query
    │
    ▼
task_decomposer.py
    │
    ├──► Sub-question 1
    ├──► Sub-question 2
    ├──► Sub-question 3
    └──► ...
             │
             ▼
      search_agent.py
   (Search per sub-question)
             │
             ▼
    summarizer_agent.py
     (Condense sources)
             │
             ▼
    factchecker_agent.py
      (Verify claims)
             │
             ▼
       ┌───────────────┐
       │ Claims flagged?│
       └───────┬───────┘
               │
          Yes  │
               ▼
       search_agent.py
    (Find more sources,
        capped retries)
               │
               └──────────────┐
                              │
                         No / Verified
                              │
                              ▼
                  report_compiler.py
                   (Compile final report)
                              │
                              ▼
                    Final Output
                     with Citations
```

## 📁 Project Structure

```text
multi-agent-research/
│
├── app/
│   ├── __init__.py
│   ├── main.py                         # Entry point (CLI/Streamlit)
│   ├── config.py                       # API keys, agent settings, max iterations
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── orchestrator.py             # Main coordination logic
│   │   ├── task_decomposer.py          # Break query into sub-questions
│   │   └── report_compiler.py          # Merge agent outputs into final report
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py               # Shared agent interface
│   │   │
│   │   ├── search_agent/
│   │   │   ├── __init__.py
│   │   │   ├── search_agent.py         # Run searches and rank sources
│   │   │   ├── search_tool.py          # Web search API wrapper
│   │   │   └── source_ranker.py        # Score sources by relevance/credibility
│   │   │
│   │   ├── summarizer_agent/
│   │   │   ├── __init__.py
│   │   │   ├── summarizer_agent.py     # Condense sources into key points
│   │   │   └── dedup.py                # Avoid duplicate points across sources
│   │   │
│   │   └── factchecker_agent/
│   │       ├── __init__.py
│   │       ├── factchecker_agent.py    # Verify claims against source text
│   │       └── claim_extractor.py      # Extract discrete claims from summaries
│   │
│   ├── communication/
│   │   ├── __init__.py
│   │   ├── message_schema.py            # Structured agent communication format
│   │   └── agent_bus.py                 # Pass messages between agents
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── llm_client.py               # Claude/GPT API wrapper
│   │   └── prompt_templates.py         # Per-agent prompt templates
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                   # Track agent decisions for debugging
│       └── citation_tracker.py         # Maintain source-to-claim mapping
│
├── data/
│   ├── research_sessions/              # Saved query, sources, and reports
│   └── cache/                          # Cached search results with TTL
│
├── tests/
│   ├── test_task_decomposer.py
│   ├── test_search_agent.py
│   ├── test_summarizer_agent.py
│   ├── test_factchecker_agent.py
│   └── test_orchestrator.py
│
├── .env                                # Environment variables
├── .env.example                        # Environment variable template
├── .gitignore
├── requirements.txt                    # Python dependencies
├── README.md
└── run.sh                              # Application startup script
```


## Setup

```bash
git clone https://github.com/masudibnmusa/Multi-Agent-Research-Assistant.git
cd multi-agent-research
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # add your API keys
```

## Usage

```bash
./run.sh
# or
python app/main.py --query "your research question here"
```

## Known Limitations / Roadmap

- **Iteration cap**: `max_iterations` in `config.py` must be enforced by `orchestrator.py`, 
  with a graceful "unverified claim" fallback instead of an infinite loop.
- **Source credibility scoring**: `source_ranker.py` needs explicit criteria (domain 
  reputation, recency, cross-source agreement) — currently underspecified.
- **Dedup vs. fact-checking order**: `dedup.py` should run *after* claim-to-source mapping, 
  not before, to avoid losing which source supports which claim.
- **Agent failure handling**: no retry/timeout/circuit-breaker logic yet in `search_tool.py` 
  or `agent_bus.py`.
- **Concurrency**: `agent_bus.py` is a simple in-memory queue — fine for single-session CLI 
  use, not yet safe for concurrent multi-user sessions.
- **Cache invalidation**: `data/cache/` needs a TTL or invalidation strategy to avoid 
  serving stale search results.

## License

MIT