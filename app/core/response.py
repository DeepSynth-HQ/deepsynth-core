from typing import Optional


class ResponseHandler:
    @staticmethod
    def success(message: str, data: Optional[dict] = None) -> dict:
        return {"message": message, "data": data}

    @staticmethod
    def error(message: str, data: Optional[dict] = None, code: int = 400) -> dict:
        return {"message": message, "data": data, "code": code}
