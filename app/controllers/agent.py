from app.services.agent import AgentService


class AgentController:
    def __init__(self, user_id: str, session_id: str = None):
        self.user_id = user_id
        self.session_id = session_id
        self.agent_service = AgentService(user_id, session_id)

    def call_agent(self, message: str, images: list[str] = []):
        return self.agent_service.call_agent(message, images)

    def get_agent_history(self):
        return self.agent_service.get_history()
