# ChatGPT Review and Handoff Workflow

This is a Control-plane workflow, not an informal copy/paste convention.

1. Codex1 creates or revises a bounded Task.
2. Codex1 creates the complete Codex2 dispatch prompt as a Markdown file in the Control repository.
3. Codex1 commits and pushes the Task and prompt.
4. User gives the Codex1 result or repository link to ChatGPT.
5. ChatGPT live-queries GitHub and independently reviews the current Control SHA, Task, prompt, scope, safety boundary, and Evidence/Result rules.
6. ChatGPT reads the committed prompt from GitHub. If valid, ChatGPT returns that exact committed artifact to User; if not, ChatGPT requests a Codex1 revision.
7. User sends the reviewed committed prompt to Codex2.

The formal handoff is the committed GitHub Markdown file. Text printed by Codex1 in a terminal or chat is informative only and is never the authoritative prompt version. Codex2 must verify the Control SHA and stop on Task/prompt scope drift.
