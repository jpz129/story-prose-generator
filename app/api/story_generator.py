# app/api/story_generator.py
from fastapi import APIRouter, HTTPException
from app.models.generation import GenerationRequest, GenerationResult
from app.services.story_generator_service import generate_prose_from_beats

router = APIRouter()

@router.get("/test")
def test_route():
    return {"message": "Router is working!"}

@router.post("/generate", response_model=GenerationResult)
def generate_story_from_beats(request: GenerationRequest):
    """
    Generate a story from a list of beats using the provided memory strategy,
    optional metadata, and evaluation settings.
    """
    try:
        result = generate_prose_from_beats(
            beats=request.beats,
            memory_strategy=request.memory_strategy,
            enable_coherence_eval=request.enable_coherence_eval,
            temperature=request.temperature,
            metadata=request.metadata.dict() if request.metadata else None,
            metadata_threshold=request.metadata_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))