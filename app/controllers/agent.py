from app.services.agent import AgentService
from log import logger


class AgentController:
    def __init__(self, user_id: str, session_id: str = None):
        self.user_id = user_id
        self.session_id = session_id
        self.agent_service = AgentService(user_id, session_id)

    def call_agent(self, message: str, images: list[str] = []):
        return self.agent_service.call_agent(message, images)

    def get_agent_history(self):
        try:
            return self.agent_service.get_history()
        except Exception as e:
            import traceback

            traceback.print_exc()
            logger.error(f"[AGENT] Failed to get history: {e}")
            return []
