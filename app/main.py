from fastapi import FastAPI, HTTPException, Depends, Request, Response
from pydantic import BaseModel, Field
from app.controllers.agent import AgentController
from app.controllers.wallet import WalletController
import uvicorn
from fastapi.responses import StreamingResponse
from config import settings
from app.middleware.limiter import RedisRateLimiterMiddleware
from app.middleware.redis import get_redis_client
from app.routes.agent import router as agent_router
from app.routes.wallet import router as wallet_router
from app.routes.file import router as file_router
from app.routes.user import router as user_router
from app.routes.wallet import router as wallet_router
from app.routes.referral import router as referral_router
from fastapi.responses import Response, JSONResponse
from app.core.error_handlers import app_exception_handler, integrity_error_handler
from app.core.exceptions import AppException
from sqlalchemy.exc import IntegrityError
from app.routes.auth import router as auth_router

app = FastAPI(
    title="DeepSynth API",
    description="API for DeepSynth",
    version="v0.1.8",
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)


@app.middleware("http")
async def cors_handler(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(
            status_code=204,
            headers={
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Origin": settings.origins,
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )
    else:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Origin"] = settings.origins
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response


PREFIX = "/api"

app.include_router(agent_router, prefix=PREFIX)
app.include_router(wallet_router, prefix=PREFIX)
app.include_router(file_router, prefix=PREFIX)
app.include_router(user_router, prefix=PREFIX)
app.include_router(wallet_router, prefix=PREFIX)
app.include_router(auth_router, prefix=PREFIX)
# app.include_router(referral_router, prefix=PREFIX)


@app.get(f"{PREFIX}/healthz")
def healthz():
    try:
        return {"message": "OK"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000)
