# ChatGPT Review and Handoff Workflow

This is a Control-plane workflow, not an informal copy/paste convention.

1. PerfControl creates or revises a bounded Task.
2. PerfControl creates the complete A3PerfRunner dispatch prompt as a Markdown file in the Control repository.
3. PerfControl commits and pushes the Task and prompt.
4. User gives the PerfControl result or repository link to ChatGPT.
5. ChatGPT live-queries GitHub and independently reviews the current Control SHA, Task, prompt, scope, safety boundary, and Evidence/Result rules.
6. ChatGPT reads the committed prompt from GitHub. If valid, ChatGPT returns that exact committed artifact to User; if not, ChatGPT requests a PerfControl revision.
7. User sends the reviewed committed prompt to A3PerfRunner.

The formal handoff is the committed GitHub Markdown file. Text printed by PerfControl in a terminal or chat is informative only and is never the authoritative prompt version. A3PerfRunner must verify the Control SHA and stop on Task/prompt scope drift.
