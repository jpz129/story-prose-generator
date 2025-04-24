# app/main.py
from fastapi import FastAPI
from app.api import story_generator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OR: ["http://localhost:4321"] for local dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes.
app.include_router(story_generator.router, prefix="/api")

# A simple health-check endpoint.
@app.get("/health")
def health_check():
    return {"status": "OK"}

print("✅ FastAPI is starting up")