# Governed Agents

> **Blueprints for the Agentic Era** — a curated gallery of autonomous AI agents that are safe to run on local machines, production databases, and sensitive APIs.

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Node9](https://img.shields.io/badge/governed%20by-Node9-6366f1)](https://node9.ai)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)](https://python.org)

---

## The Governance Paradigm

Traditional AI agents are locked in sandboxes — restricted, isolated, and ultimately unable to do real work. **Governed Agents takes a different approach.**

Instead of caging the agent, we give it a **Sudo layer**.

> *"Node9 redefines the relationship between humans and AI by acting as a deterministic Gatekeeper — the first 'Sudo' layer built specifically for the Agentic Era. Instead of forcing agents into restrictive sandboxes that break local workflows, Node9 allows agents to operate with full local capabilities while placing a mandatory human signature on every high-risk execution."*

The key insight: a **blocking event is a collaboration opportunity**. Through the AI Negotiation Loop, Node9 doesn't just cut the wire — it gives the agent structured feedback, teaches it why an action was blocked, and guides it toward a safer alternative.

This creates **Governed Autonomy**: the AI provides the speed, the human provides the strategy and the final "Yes."

---

## Agent Gallery

| Agent | Purpose | Governance Logic |
|-------|---------|-----------------|
| [Marketing Agent](./governed_marketing_agent.py) | Autonomous content creation | Intercepts `medium_publish` calls — human approves or denies the post via Slack / Terminal before any draft goes live |
| Safe SQL Admin *(coming soon)* | Natural language DB management | Allows `SELECT` and `INSERT` globally; triggers a Race for Approval on `DROP`, `TRUNCATE`, or `DELETE` |
| DevOps Guard *(coming soon)* | Shell-based infrastructure automation | Governs sensitive bash commands; blocks unauthorized access to `.env` or `~/.ssh` |

---

## Quickstart: Marketing Agent

The marketing agent researches recent AI security news and drafts a Medium blog post — then **pauses and asks for your approval** before publishing anything.

### 1. Install Node9

```bash
npm install -g @node9/proxy
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your tokens
```

| Variable | Description |
|----------|-------------|
| `MEDIUM_TOKEN` | Medium integration token — Settings → Security → Integration tokens |
| `MEDIUM_AUTHOR_ID` | Your Medium user ID — `curl -H "Authorization: Bearer <token>" https://api.medium.com/v1/me` |
| `TAVILY_API_KEY` | Tavily search API key — [tavily.com](https://tavily.com) |
| `ANTHROPIC_API_KEY` | Anthropic API key — [console.anthropic.com](https://console.anthropic.com) |

### 4. Run with governance

```bash
python governed_marketing_agent.py
```

When the agent is ready to publish, **Node9 will pause execution** and send an approval request to your configured channel (Slack, Terminal popup, or the Node9 dashboard). You decide — the agent waits.

---

## How Governance Works

The `@protect` decorator from the Node9 SDK is the single line that transforms a risky autonomous action into a governed one:

```python
from node9 import protect, ActionDeniedException

@tool("publish_to_medium")
@protect("medium_publish")          # ← Node9 intercepts here
def publish_to_medium(title, content):
    """Publishes a draft to Medium."""
    ...
```

When the agent calls `publish_to_medium`:

1. **Node9 intercepts** the call before any code runs
2. **A race starts** — approval request fires to Slack, Terminal popup, and the Node9 dashboard simultaneously
3. **First responder wins** — approve or deny from any channel
4. **If approved** — execution continues, draft is created on Medium
5. **If denied** — `ActionDeniedException` is raised, nothing is published, the agent is told why

---

## Contributing

Have you built an agent you finally feel safe running locally? Submit a Pull Request.

Each agent submission should include:
- The agent script with `@protect` on all high-risk tools
- A brief description of what it governs and why
- A `.env.example` with required variables

**Help us build the world's largest library of Governed AI.**

> *"Stop fearing the execution. Start governing it."*

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
