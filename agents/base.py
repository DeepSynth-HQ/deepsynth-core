from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model.google import Gemini
from phi.storage.agent.postgres import PgAgentStorage
from tools.image_analyzer import analyze_image
from tools.search import search
from config import settings
from rich import print
from log import logger
from rich.console import Console
from rich.json import JSON
from tools.onchain import OnchainTool


from phi.model.openai import OpenAIChat
from uuid import uuid4
from app.services.wallet import WalletService
from app.database.client import get_db
from sqlalchemy.orm import Session
from prompt_engineering.deepsynth import DeepSynthPromptEngineering


from agents.models.llama import LlamaChat

db_url = settings.POSTGRES_URL
storage = PgAgentStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_url: Postgres database URL
    db_url=db_url,
)

console = Console()


class BaseAgent:
    user_id: str
    session_id: str

    def __init__(self, user_id: str, session_id: str = None):
        self.user_id = user_id
        self.session_id = session_id
        logger.debug(f"[AGENT] User ID: {self.user_id}")
        logger.debug(f"[AGENT] Session ID: {self.session_id}")

    def get_history(self):
        logger.info(
            f"Getting history for session {self.session_id} and user {self.user_id}"
        )
        sessions = storage.get_all_sessions(user_id=self.user_id)
        history = []
        if self.session_id:
            session = next((s for s in sessions if s.session_id == session_id), None)
            if session is None:
                logger.info(f"No session found for {session_id} and user {user_id}")
                return history
            for run in session.memory.get("runs"):
                user_message = run.get("message").get("content")
                created_at = run.get("message").get("created_at")
                images_message = [
                    message.get("images")
                    for message in run.get("response").get("messages")
                    if message.get("role") == "user"
                ][0]
                agent_message = run.get("response").get("content")
                result = [
                    {
                        "role": "user",
                        "content": user_message,
                        "images": images_message,
                        "session_id": session.session_id,
                        "created_at": created_at,
                    },
                    {
                        "role": "assistant",
                        "content": agent_message,
                        "session_id": session.session_id,
                    },
                ]
                history.extend(result)
            return history
        else:
            all_sessions = []
            for session in sessions:
                history = []
                session_id = session.session_id
                for run in session.memory.get("runs"):
                    user_message = run.get("message").get("content")
                    created_at = run.get("message").get("created_at")
                    agent_message = run.get("response").get("content")
                    history.extend(
                        [
                            {
                                "role": "user",
                                "content": user_message,
                                "session_id": session_id,
                                "created_at": created_at,
                            },
                            {
                                "role": "assistant",
                                "content": agent_message,
                                "session_id": session_id,
                            },
                        ]
                    )
                all_sessions.append(history)
            return all_sessions

    def run(
        self,
        message: str,
        images: list[str] = [],
        stream: bool = False,
        db: Session = None,
    ):
        if db is None:
            db = next(get_db())

        tools = [
            search,
            analyze_image,
            OnchainTool(),
        ]
        deepsynth_agent = Agent(
            name="DeepSynth",
            tools=tools,
            # model=OpenAIChat(id="gpt-4o-mini", temperature=0.3, max_tokens=16000),
            model=LlamaChat(
                id=settings.ATOMA_LLAMA_3_3_70B_INSTRUCT,
                base_url=settings.ATOMA_BASE_URL,
                api_key=settings.ATOMA_API_KEY,
            ),
            description=DeepSynthPromptEngineering().get_description(),
            instructions=DeepSynthPromptEngineering().get_instructions(),
            # show_tool_calls=True,
            markdown=True,
            storage=storage,
            read_chat_history=True,
            session_id=self.session_id,
            num_history_responses=5,
            add_chat_history_to_messages=True,
            user_id=self.user_id,
            debug_mode=True,
            add_datetime_to_instructions=True,
            read_tool_call_history=True,
            additional_context=f"You own the wallet with address: {WalletService(db).get_wallet_by_user_id(self.user_id).public_key if self.user_id else None}",
            context={
                "user_id": self.user_id,
                "session_id": self.session_id,
            },
        )
        # multi_agent_team.print_response(message=message + " " + "\n".join(images), stream=stream, markdown = True)
        return deepsynth_agent.run(
            message=message + " " + "\n".join(images), stream=stream
        )


if __name__ == "__main__":
    # Chạy hàm call_agent với các tham số mẫu
    user_id = "50c96bb8-359e-4adf-bec7-4532895b2bbb"
    session_id = str(uuid4())
    while True:
        message = input("💥>  ")
        if message in ["q", "exit"]:
            break
        response = BaseAgent(user_id=user_id, session_id=session_id).run(
            message=message, stream=True
        )
        aggregated_response = ""
        for chunk in response:
            aggregated_response += chunk.content
        print(f"🗯️>   {aggregated_response}")
