from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, discovery, matches, messages, profiles, stats, swipes

app = FastAPI(title="Finder API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
app.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
app.include_router(swipes.router, prefix="/swipes", tags=["swipes"])
app.include_router(matches.router, prefix="/matches", tags=["matches"])
app.include_router(messages.router, tags=["messages"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
