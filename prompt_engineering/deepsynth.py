from prompt_engineering.base import BasePromptEngineering
from config import settings


class DeepSynthPromptEngineering(BasePromptEngineering):
    description = settings.DEEPSYNTH_DESCRIPTION_PROMPT
    instructions = settings.DEEPSYNTH_INSTRUCTION_PROMPT
    system_prompt = settings.DEEPSYNTH_SYSTEM_PROMPT

    def __init__(self):
        super().__init__(
            description=self.description,
            instructions=self.instructions,
            system_prompt=self.system_prompt,
        )


if __name__ == "__main__":
    print(DeepSynthPromptEngineering().get_description())
