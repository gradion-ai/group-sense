from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.google import GoogleModelSettings

SYSTEM_PROMPT = """Provide a consice, direct answer to a query.
Always pretend you know the answer to a query.
If an answer requires real-time information, fake it."""


class Service:
    def __init__(self):
        self._instances: dict[str, Agent] = {}

    async def run(self, query: str, sender: str) -> str:
        instance = self.get_instance(sender)
        return await instance.run(query)

    def get_instance(self, sender: str) -> Agent:
        if sender not in self._instances:
            self._instances[sender] = Assistant()
        return self._instances[sender]


class Assistant:
    def __init__(self):
        self._history: list[ModelMessage] = []
        self._agent = Agent(
            system_prompt=SYSTEM_PROMPT,
            model="google-gla:gemini-2.5-flash",
            model_settings=GoogleModelSettings(
                google_thinking_config={
                    "thinking_budget": 0,
                }
            ),
        )

    async def run(self, query: str) -> str:
        result = await self._agent.run(query, message_history=self._history)
        self._history = result.all_messages()
        return result.output
