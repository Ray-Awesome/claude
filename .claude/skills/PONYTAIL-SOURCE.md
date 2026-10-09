# Ponytail skills

Vendored from https://github.com/DietrichGebert/ponytail at commit 9cc65d0 (v5.1.0, MIT License, see PONYTAIL-LICENSE).

The skills live in `.claude/skills/ponytail*`. The upstream plugin's hooks are copied to `.claude/ponytail-hooks/` and registered in `.claude/settings.json` (SessionStart, SubagentStart, UserPromptSubmit). They read `../skills/ponytail/SKILL.md` relative to that folder, make no network calls, and write small mode/flag files under `~/.claude` and `~/.config/ponytail`.

Turn it off for a session with "stop ponytail" or `/ponytail` levels `lite|full|ultra`. To update: copy upstream `skills/` and `hooks/*.js` over these.
