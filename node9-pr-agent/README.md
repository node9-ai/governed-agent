# CI Code Review Agent

An autonomous CI agent that reviews pull requests, fixes bugs, and posts a dedicated security review — all governed by [node9](https://node9.ai).

[![Node9](https://img.shields.io/badge/governed%20by-Node9-6366f1)](https://node9.ai)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab)](https://python.org)

---

## What It Does

On every push to a non-main branch, the agent runs a four-step pipeline:

| Step | What happens |
|------|-------------|
| **1. Fix loop** | Reads changed files, fixes real bugs, runs tests (up to 6 turns) |
| **2. Safety check** | Reverts AI changes if tests break after fixes |
| **3. Code review** | Reviews the agent's own fixes — posts as `🔍 node9 Code Review` on your PR |
| **4. Security review** | Data-flow pass on the original diff — posts as `🔒 node9 Security Review` on your PR |

**Two possible outcomes:**

- **Agent found nothing to fix** — one PR (yours), two review comments on it
- **Agent fixed bugs** — your PR gets review comments + a separate `[node9] AI fixes` PR with the agent's changes for you to review

---

## Install in Your Repo

### 1. Copy the agent files

```bash
mkdir -p .github/node9
cp ci-code-review-fixer/agent.py .github/node9/
cp ci-code-review-fixer/tools.py .github/node9/
cp ci-code-review-fixer/requirements.txt .github/node9/
```

### 2. Add the workflow

Create `.github/workflows/node9-review.yml`:

```yaml
name: node9 CI Code Review

on:
  push:
    branches-ignore:
      - main
      - 'node9/fix/**'
  workflow_dispatch:

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        working-directory: .github/node9
        run: pip install -r requirements.txt

      - name: Run node9 CI review
        working-directory: .github/node9
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          NODE9_API_KEY:     ${{ secrets.NODE9_API_KEY }}
          NODE9_TEST_CMD:    ${{ vars.NODE9_TEST_CMD || 'npm test' }}
          GITHUB_TOKEN:      ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          GITHUB_HEAD_REF:   ${{ github.ref_name }}
          GITHUB_BASE_REF:   ${{ github.event.repository.default_branch || 'main' }}
          GITHUB_WORKSPACE:  ${{ github.workspace }}
        run: python agent.py
```

### 3. Set secrets

In your repo: **Settings → Secrets and variables → Actions**

| Secret | Required | Description |
|--------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key — [console.anthropic.com](https://console.anthropic.com) |
| `NODE9_API_KEY` | No | node9 SaaS key for audit trail — [node9.ai](https://node9.ai) |

### 4. Set the test command (optional)

In **Settings → Variables → Actions**, set `NODE9_TEST_CMD` to your test command.  
Default: `npm test`

Examples: `pytest`, `cargo test`, `go test ./...`

---

## What You'll See

After each push to a feature branch, the agent posts two comments on your PR:

**`🔍 node9 Code Review`** — logic and correctness review of the agent's own fixes (or the original diff if no fixes were needed)

**`🔒 node9 Security Review`** — focused data-flow analysis of the original PR diff, looking for:
- User-controlled inputs reaching filesystem sinks (`path.join`, `open()`)
- Execution sinks (`exec`, `spawn`, `subprocess`)
- Network sinks (URLs constructed from input)
- Deserialization of untrusted input
- Validation gaps (blocklist vs allowlist, unanchored regex)

Findings are rated **HIGH / MEDIUM / LOW**.

---

## Security Model

The agent runs with `node9` in `audit` mode — every tool call (file read, file write, bash command) is logged to the node9 audit trail.

**Prompt injection mitigations:**
- Security review instructions live in the system message, separate from the untrusted diff
- The diff is explicitly labelled as untrusted data in the user message
- Model output is scanned for `GITHUB_TOKEN`, `ANTHROPIC_API_KEY`, and `NODE9_API_KEY` before posting to GitHub

**Tool safety:**
- File reads and writes are sandboxed to `GITHUB_WORKSPACE` via `safe_path()`
- Tool inputs are validated against an allowlist before dispatch
- `read_code('.')` lists the workspace root safely instead of crashing

---

## Configuration

| Environment variable | Default | Description |
|---------------------|---------|-------------|
| `NODE9_TEST_CMD` | `npm test` | Command to run tests |
| `GITHUB_BASE_REF` | `main` | Base branch to diff against |
| `GITHUB_HEAD_REF` | current branch | Branch being reviewed |

---

## License

Apache 2.0 — see [LICENSE](../LICENSE).
