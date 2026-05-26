# Agent Protocol — AI Law Assistant

> **Every agent session MUST follow this protocol.**

## On Session Start

1. **READ** `PROJECT_KNOWLEDGE.md` in the project root — this is your full context
2. **CHECK** `task.md` — the shared task tracker at:
   ```
   C:\Users\annao\.gemini\antigravity-ide\brain\8c66e108-6ce3-452a-ba7b-0367addfe051\task.md
   ```
   This file contains the project roadmap as a trackable checklist. Review it to see what's planned, in-progress, or completed.
3. Do NOT re-analyze files that are already documented in `PROJECT_KNOWLEDGE.md`
4. If a file has changed since the knowledge base was last updated, note the discrepancy

## During Work

1. Follow the conventions documented in `PROJECT_KNOWLEDGE.md` Section 7
2. Match existing code style and patterns
3. Test changes using the existing `scratch/` test scripts as reference
4. **Update `task.md`** as you work:
   - Mark items `[/]` when you start working on them
   - Mark items `[x]` when completed
   - Add new sub-tasks if needed

## On Session End (After Making Changes)

1. **UPDATE** `PROJECT_KNOWLEDGE.md`:
   - Update file semantics if you added/modified/deleted files (Section 2)
   - Update current state if you fixed bugs or broke things (Section 8)
   - Update roadmap if you completed planned items (Section 10)
   - **APPEND** a row to the Change Log (Section 9) with date, author, and summary

2. Format for Change Log entries:
   ```
   | YYYY-MM-DD | Agent Name | Brief description of what changed |
   ```

## Key Rules

- **Never skip reading PROJECT_KNOWLEDGE.md** — it saves you 15K+ tokens of redundant file reading
- **Never leave PROJECT_KNOWLEDGE.md stale** — update it even for small changes
- **Architecture decisions go in the knowledge base** — don't bury rationale in commit messages only
- **Design token changes must update Section 3** — the design system section is the frontend's source of truth
- **API changes must update Section 4** — other agents and frontend code depend on this reference

## Jules Sessions

When creating Jules sessions via MCP:
- Include a summary of the task in the Change Log
- Reference the session ID so future agents can look up the diff via `jules_list_sessions`
