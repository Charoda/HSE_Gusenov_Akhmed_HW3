from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth_router import router as auth_router
from app.api.links_router import router as links_router
from app.config import settings
from app.initialization import init_app

app = FastAPI(
    title="URL Shortener API",
    description="A service for shortening URLs with analytics and management features",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_app()

app.include_router(auth_router)
app.include_router(links_router)

@app.get("/")
async def root():
    return {"message": "URL Shortener API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}