# app/main.py
from fastapi import FastAPI
from app.api import story_generator

app = FastAPI()

# Include API routes.
app.include_router(story_generator.router, prefix="/api")

# A simple health-check endpoint.
@app.get("/health")
def health_check():
    return {"status": "OK"}

print("✅ FastAPI is starting up")