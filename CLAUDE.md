# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

```bash
uv sync                      # Install/sync dependencies
uv add <dep>                 # Add dependency (--dev for dev deps)
uv run invoke cc             # Run code checks (auto-fixes formatting, mypy errors need manual fix)
uv run invoke test           # Run all tests
uv run invoke ut             # Run unit tests only
uv run invoke it             # Run integration tests only
uv run invoke test --cov     # Run tests with coverage

# Single test file
uv run pytest -xsv tests/integration/test_[name].py

# Single test
uv run pytest -xsv tests/integration/test_[name].py::test_name

# Documentation
uv run invoke build-docs     # Build docs
uv run invoke serve-docs     # Serve docs at localhost:8000
```

**Note:** `invoke cc` only checks files under version control. Run `git add` on new files first.

## Overview

The `group_sense` package is a library for detecting patterns in group chat message streams and transforming them into self-contained queries for downstream AI systems. This enables existing single-user AI agents to participate in group conversations based on configurable criteria, without requiring training on multi-party conversations.

## Key Modules and Classes

### `group_sense.message`
Core data structures for group chat messages:
- `Message`: Represents a single group chat message with content, sender/receiver IDs, thread references, and attachments
- `Attachment`: Metadata for media or documents attached to messages (file paths, display names, MIME types)
- `Thread`: Reference to related discussions in other group chat threads

### `group_sense.reasoner.base`
Abstract protocols and response types:
- `GroupReasoner`: Protocol for incremental message processors that maintain conversation context across multiple `process()` calls
- `GroupReasonerFactory`: Protocol for factories that create reasoner instances customized for specific owners
- `Response`: Triage decision response containing a `Decision` (DELEGATE or IGNORE) and optional delegation parameters
- `Decision`: Enum determining whether messages should be processed or ignored

### `group_sense.reasoner.default`
Default single-context implementation:
- `DefaultGroupReasoner`: Processes group chat messages using a single reasoner agent instance with shared conversation state across all senders. All messages are added to the same conversation history. Supports state serialization.
- `DefaultGroupReasonerFactory`: Creates `DefaultGroupReasoner` instances with owner-specific system prompts by substituting `{owner}` placeholders

### `group_sense.reasoner.concurrent`
Concurrent per-sender processing:
- `ConcurrentGroupReasoner`: Manages multiple group reasoner instances (one per sender) with independent conversation states. All instances see the same message history, but maintain separate conversation contexts.
