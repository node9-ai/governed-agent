"""
Node9 Governed Marketing Agent
------------------------------
This autonomous agent uses CrewAI and Tavily to research AI security news
and draft technical blog posts for Medium.

Governance:
  The 'publish_to_medium' tool is wrapped with the Node9 @protect decorator.
  When the agent calls this tool, Node9 intercepts the execution and sends an
  approval request via the Race Engine (Slack / Terminal popup). The post is
  only published if a human approves it.

  If the human denies the request, Node9 raises ActionDeniedException, which
  is caught here and logged as a security event.

  NOTE: CrewAI catches tool-level exceptions internally and returns them as
  tool error strings to the agent. To ensure ActionDeniedException propagates
  out of the Crew, it inherits from BaseException in the node9 SDK — so it
  bypasses CrewAI's except Exception handlers and surfaces here correctly.

Requirements:
  pip install -r requirements.txt

Run:
  python governed_marketing_agent.py
"""
import os
import sys
import requests
import json

from node9 import protect, ActionDeniedException
from crewai import Agent, Task, Crew
from crewai.tools import tool


# ---------------------------------------------------------------------------
# Startup validation — fail fast with a clear message rather than mid-run
# ---------------------------------------------------------------------------

_REQUIRED_ENV = {
    "MEDIUM_TOKEN": "Your Medium integration token (Settings → Security → Integration tokens)",
    "MEDIUM_AUTHOR_ID": "Your Medium user ID — run: curl -H 'Authorization: Bearer <token>' https://api.medium.com/v1/me",
    "TAVILY_API_KEY": "Your Tavily API key — https://tavily.com",
    "ANTHROPIC_API_KEY": "Your Anthropic API key — https://console.anthropic.com (used by CrewAI)",
}

_missing = [k for k in _REQUIRED_ENV if not os.getenv(k)]
if _missing:
    print("❌  Missing required environment variables:")
    for key in _missing:
        print(f"   {key}: {_REQUIRED_ENV[key]}")
    print("\nCopy .env.example to .env, fill in the values, and re-run.")
    sys.exit(1)

MEDIUM_TOKEN = os.environ["MEDIUM_TOKEN"]
MEDIUM_AUTHOR_ID = os.environ["MEDIUM_AUTHOR_ID"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool("web_search")
def web_search(query: str) -> str:
    """Search the internet for the latest news and technical articles."""
    from tavily import TavilyClient
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily.search(query=query, search_depth="advanced")
    return json.dumps(response["results"])


# @protect must be the innermost decorator so Node9 intercepts the raw
# function call. @tool (outermost) wraps the already-protected function
# and registers it with CrewAI, preserving the docstring via functools.wraps.
@tool("publish_to_medium")
@protect("medium_publish")
def publish_to_medium(title: str, content: str) -> str:
    """Publishes a post to Medium as a DRAFT. Requires human approval via Node9."""
    url = f"https://api.medium.com/v1/users/{MEDIUM_AUTHOR_ID}/posts"
    headers = {
        "Authorization": f"Bearer {MEDIUM_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "title": title,
        "contentFormat": "markdown",
        "content": content,
        "publishStatus": "draft",  # Safety net: always draft, never direct publish
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return "SUCCESS: Draft created on Medium. Check your Medium dashboard to review and publish."
    return f"FAILED: {response.status_code} - {response.text}"


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------

researcher = Agent(
    role="Tech Researcher",
    goal="Find the most relevant and recent news about AI Agent security and terminal risks.",
    backstory="Expert at finding real-world examples of AI agents making dangerous mistakes in production environments.",
    tools=[web_search],
    verbose=True,
    allow_delegation=False,
)

writer = Agent(
    role="Technical Content Strategist",
    goal="Write a compelling Medium blog post that positions Node9 as the essential safety layer for AI agents.",
    backstory="Specializes in writing viral technical content for developers on Medium. Understands how to blend security narratives with practical developer problems.",
    tools=[publish_to_medium],
    verbose=True,
    allow_delegation=False,
)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

task_research = Task(
    description=(
        "Search for news from the last 7 days about: "
        "'AI Agent hallucinations terminal commands', "
        "'Claude Code dangerous shell commands', "
        "'Devin AI security incident', "
        "'agentic AI security risks 2025'. "
        "Find 3 high-impact, real stories that show why ungoverned AI agents are dangerous."
    ),
    expected_output="A list of 3 high-impact news stories with titles, sources, and 2-3 sentence summaries.",
    agent=researcher,
)

task_write = Task(
    description=(
        "1. Use the research results to write a compelling 600-word Medium post in Markdown.\n"
        "2. Title: 'Why Your AI Agent Needs a Sudo: The Node9 Story'\n"
        "3. Structure: hook (real incident) → problem → Node9 solution → Governance Paradigm → CTA.\n"
        "4. Weave in the 3 research stories as concrete examples.\n"
        "5. End with a call-to-action to try Node9: https://node9.ai\n"
        "6. Call the 'publish_to_medium' tool to save the post as a draft.\n"
        "   Node9 will pause execution and ask for your approval before anything is sent."
    ),
    expected_output="The full blog post in Markdown and a confirmation that the draft was uploaded.",
    agent=writer,
)


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_marketing_workflow():
    marketing_crew = Crew(
        agents=[researcher, writer],
        tasks=[task_research, task_write],
        verbose=True,
    )

    print("--- Starting Node9 Weekly Marketing Agent ---")
    print("Node9 will pause and ask for your approval before publishing.\n")

    try:
        # Node9 intercepts the 'publish_to_medium' call during kickoff.
        # Execution blocks here until you approve or deny via Slack/Terminal.
        result = marketing_crew.kickoff()
        print("\n\n########################")
        print("##  WORKFLOW COMPLETE  ##")
        print("########################\n")
        print(result)

    except ActionDeniedException as e:
        # Human denied the publish action via the Node9 Race Engine.
        print(f"\n🚨 Publish blocked by Node9: {e.reason}")
        print("The draft was NOT sent to Medium. No action was taken.")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    run_marketing_workflow()
