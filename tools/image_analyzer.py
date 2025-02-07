from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings
from typing import List

from phi.tools import Toolkit
from phi.utils.log import logger
from phi.agent import Agent

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_tokens=8192,
    api_key=settings.GEMINI_API_KEY,
)


def analyze_image(url: str, query: str, user_id: str) -> str:
    """
    Use this tool to analyze images to extract features, identify objects, and provide a detailed description of the image. It is also useful for providing investment strategies related to the identified elements.

    Args:
        urls (str):  URL to image for analysis.
        query (str): Query string to guide the analysis.
        user_id (str): User ID to identify the user.

    Returns:
        str: Result of the image analysis.
    """

    logger.info(f"[TOOLS] Analyzing image: {url} for user: {user_id}")
    try:
        import ast

        user_message_content = []
        user_message_content.append({"type": "text", "text": query})
        user_message_content.append({"type": "image_url", "image_url": {"url": url}})
        messages = [
            {
                "role": "system",
                "content": settings.DEEPSYNTH_IMAGE_ANALYSIS_SYSTEM_PROMPT,
            },
            {"role": "user", "content": user_message_content},
        ]
        response = model.invoke(messages).content
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}
