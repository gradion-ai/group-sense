# Group Sense

## Introduction

Group Sense detects patterns in group chat message streams and transforms them into self-contained queries for downstream AI systems. While single-user AI assistants excel at responding to direct queries, they struggle with multi-party conversations where relevant information emerges from complex exchanges between multiple participants. Group Sense solves this by acting as an intelligent adapter that monitors group conversations, identifies meaningful patterns, and reformulates them into queries that existing AI assistants can process, enabling proactive and "overhearing" AI assistance without requiring the underlying assistant to understand group dynamics or multi-party dialogue structure.

The library provides three core capabilities that make group chat AI assistance practical and flexible. First, it detects conversation patterns and transforms multi-party dialogue into self-contained queries that preserve essential context while removing conversational complexity. Second, engagement criteria are defined in natural language rather than code, allowing you to specify when and how the AI should participate using clear, human-readable rules. Third, Group Sense works as a non-invasive adapter for any existing single-user AI assistant or agent: no modification, retraining, or specialized models required. This architecture lets you add group chat capabilities to AI systems you already use, whether for collaborative decision-making, team coordination, or ambient assistance scenarios.

## Documentation

- [Installation](https://gradion-ai.github.io/group-sense/installation/): Installation instructions and API key setup
- [Basics](https://gradion-ai.github.io/group-sense/basics/) Core concepts and reasoner types
- [Examples](https://gradion-ai.github.io/group-sense/examples/): Usage examples for different engagement patterns
- [Integration](https://gradion-ai.github.io/group-sense/integration/): Integrating Group Sense into applications
- [API Documentation](https://gradion-ai.github.io/group-sense/api/message/): Complete API reference

## LLM-Readable Documentation

For AI assistants and LLM-based tools, optimized documentation formats are available:

- [llms.txt](https://gradion-ai.github.io/group-sense/llms.txt): Concise documentation suitable for LLM context windows
- [llms-full.txt](https://gradion-ai.github.io/group-sense/llms-full.txt): Complete documentation with full API details

## Development

For development setup, see [DEVELOPMENT.md](DEVELOPMENT.md)
```
