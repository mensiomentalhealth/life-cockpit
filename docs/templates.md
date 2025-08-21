# Template System

Reusable, versioned content templates to generate messages, Dataverse notes, and API payloads from context data.

## What it is (v1)

- Reusable files in the repo that render with variables into:
  - Email/Teams/Telegram message subjects/bodies
  - Dataverse notes (annotations)
  - Simple JSON payloads (future)
- Rendered with a lightweight engine (Jinja2) using your runtime context.
- Tracked in git; portable across environments; previewable in dry-run.

## Why

- Consistent language and formatting
- Safe preview via dry-run before writes
- Easy iteration and rollback (git history)

## Where files live

```
templates/
  messages/
    email/
      session-summary.md
  notes/
    session-summary.md
  workflows/
    example.yaml   # future
```

## File format

- Markdown (for messages/notes) with YAML front matter for metadata
- JSON/YAML (for payload templates) planned for future

### YAML front matter keys

- name: short identifier
- version: semver for template
- type: message | note | payload
- channels: [email, teams, telegram] (for messages)
- entity: account | contact | cre92_scheduledmessage | … (for notes)
- required_vars: [client_name, session_date, …]
- defaults: key/value fallback variables
- preview_samples: optional example context for previews

Example:

```markdown
---
name: session-summary
version: 1.0.0
type: note
entity: account
required_vars:
  - client_name
  - session_date
defaults:
  signature: "— Mensio"
---
# Session Summary for {{ client_name }}

Date: {{ session_date }}

{{ summary_text }}

{{ signature }}
```

## Rendering engine

- Jinja2 with safe filters (escape by default)
- Context provided at runtime (from CLI or calling code)
- Missing required_vars → validation error (no render)

## How you’ll use it (v1)

- CLI: soon
  - `blc templates:list`
  - `blc templates:render <name> --data-file context.json`
- Existing verbs integration (planned)
  - `blc dv note <logical> <id> --template session-summary --data-file ctx.json`
  - `blc messaging send --template <name> --to <address> --data-file ctx.json`

## Governance

- Dry-run first: show rendered output, do not write
- Approval gate required for writes in protected classifications
- All renders/writes logged with run IDs

## Roadmap

- v1: notes/messages with Markdown + YAML front matter, Jinja2 render
- v1.1: payload templates (JSON/YAML) for API bodies
- v1.2: template registry cache + `templates:` CLI
- v2: UI previews in web dashboard

## Minimal implementation tasks

- Add `templates/` folders and first `session-summary.md` example
- Add Jinja2 dependency
- Implement `templates` helper (load/validate/render)
- Wire into `dv note` and messaging send (optional `--template`)
- Add docs and tests
