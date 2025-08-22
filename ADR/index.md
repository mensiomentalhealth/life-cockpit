# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Life Cockpit project.

## What is an ADR?
An ADR documents a significant architectural decision made along with its context and consequences.

## ADR Template
See [template.md](template.md) for the standard ADR format.

## ADRs

### 001 - Terminal-First Architecture (Pending)
- Status: Proposed
- Decision: All business logic exposed as CLI verbs first, UI second
- Date: 2025-01

### 002 - L0-L4 Layered Architecture (Pending)
- Status: Accepted
- Decision: Organize code into L0 (Infra), L1 (Shim), L2 (Domain), L3 (CLI), L4 (Workflows)
- Date: 2025-01

### 003 - Policy-as-Code (Pending)
- Status: Accepted
- Decision: Enforce all rules via code (validators, linters, tests) not documentation
- Date: 2025-01

## How to Add a New ADR
1. Copy `template.md` to `NNN-title.md` (e.g., `004-database-choice.md`)
2. Fill in the template sections
3. Update this index
4. Submit PR for review
