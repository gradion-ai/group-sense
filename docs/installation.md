# Installation

## Python Package

```bash
pip install group-sense
```

## Development Setup

For development setup and contributing guidelines, see [DEVELOPMENT.md](https://github.com/gradion-ai/group-sense/blob/main/DEVELOPMENT.md).

## API Keys

Group Sense uses Google Gemini models by default. Set your API key:

```bash
export GOOGLE_API_KEY="your-api-key"
```

The library supports any [pydantic-ai](https://ai.pydantic.dev/) compatible model. Pass a custom model to reasoner constructors using the `model` parameter.
