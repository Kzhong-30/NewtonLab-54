from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .api import auth, scripts, games, reviews, dm, community


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="剧本杀平台 API",
    description="一个完整的剧本杀平台后端服务，提供用户认证、剧本管理、游戏组织、DM管理、评价系统和社区功能。",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(scripts.router, prefix="/api", tags=["剧本"])
app.include_router(games.router, prefix="/api", tags=["游戏"])
app.include_router(reviews.router, prefix="/api", tags=["评价"])
app.include_router(dm.router, prefix="/api", tags=["DM"])
app.include_router(community.router, prefix="/api", tags=["社区"])


@app.get("/health", summary="健康检查")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}


@app.get("/", summary="项目信息")
async def root():
    return {
        "name": "剧本杀平台 API",
        "version": "1.0.0",
        "description": "一个完整的剧本杀平台后端服务",
        "docs": "/docs",
        "api_prefix": "/api",
    }
