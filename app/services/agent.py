from agents.base import BaseAgent


class AgentService:
    def __init__(self, user_id: str, session_id: str = None):
        self.user_id = user_id
        self.session_id = session_id
        self.agent = BaseAgent(user_id=user_id, session_id=session_id)

    def call_agent(
        self,
        message: str,
        images: list[str] = [],
        stream: bool = True,
    ):
        response = self.agent.run(
            message=message,
            images=images,
            stream=stream,
        )
        return response

    def get_history(self):
        return self.agent.get_history()
