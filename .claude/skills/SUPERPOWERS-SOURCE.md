# Superpowers skills

Vendored from https://github.com/obra/superpowers at commit 8ca22db (MIT License, see SUPERPOWERS-LICENSE).

To update: clone the upstream repo and copy its `skills/` directory over this one.

The upstream plugin also ships a SessionStart hook that injects the `using-superpowers` skill into every session. Without it the skills are listed but rarely invoked. It lives at `.claude/hooks/superpowers-session-start` (copied from upstream `hooks/session-start`) and is registered in `.claude/settings.json`.
