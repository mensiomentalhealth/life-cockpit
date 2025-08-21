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


