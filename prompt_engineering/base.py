from typing import Optional
import re


class BasePromptEngineering:
    description: str
    instructions: str
    system_prompt: str
    tools: list[str]

    def __init__(
        self,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.description = description
        self.instructions = instructions
        self.system_prompt = (
            system_prompt
            or f"""
        {description}
        {instructions}
        """
        )

    def get_instructions(self):
        return self.instructions

    def get_description(self):
        return self.description

    def get_system_prompt(self):
        return self.system_prompt
