from contextlib import asynccontextmanager

from api.routes import init_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db


def create_app() -> FastAPI:        
    cors_origins = [
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db()
        yield

    app = FastAPI(
        title="Teste Pedro Garcia",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    init_routes(app)

    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api:create_app", host="127.0.0.1", port=8000, reload=True, factory=True)