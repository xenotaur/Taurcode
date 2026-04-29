# AGENTS.md

This repository is the home of **Taurcode**.

Taurcode is a lightweight toolkit for managing AI assistance prompts and exporting them to
packages such as Espanso.

## Mission

Build a command line utility that can:

1. Define an storage format for prompts that is easy for humans to read and machines to validate.
2. Export them to packages like Espanso.
3. Backport an Espanso package into our format.

## Architectural boundary

Keep clear separation between:

1. **the tool code** in `src/taurcode/`
2. **package tests** in `tests/`
3. **the project control plane** in `project/`

## Current implementation priority

Focus first on the most useful command line utility:

1. Create the taurcode utility
2. Export samples in espanso format
3. Show that a round trip back works
4. Add other features until it's super convenient.

## Repository conventions

### Project schema

Taurcode uses a Logical Robotics Harness (LRH) control-plane schema. This project control stack contains:

**Principles → Project Goal → Roadmap → Current Focus → Work Items → Evidence → Status**

Taurcode does not need to manage this state; it is run by the LRH command or the human user. LRH tooling is used to create and manage this state in the project directory.

## Engineering style

- Prefer readable, explicit Python.
- Prefer modular organization by concern.
- Avoid hidden magic in repo discovery.
- Keep formats stable and documented.

## Immediate task guidance

When asked to make progress in this repository, prefer work that advances the first validation path:

1. Create the taurcode utility
2. Export samples in espanso format
3. Show that a round trip back works
4. Add other features until it's super convenient.


## Prompt-driven work

When a task is driven by a generated prompt, follow `PROMPTS.md` for prompt IDs, execution records, rerun handling, and optional work-item traceability. Do not create prompt records for trivial or purely exploratory work unless asked.
