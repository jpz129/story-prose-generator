# app/models/generation.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class BeatEvaluation(BaseModel):
    beat_index: int
    word_count: int
    length_ok: bool
    beat_coverage_score: float

class CoherenceEvaluation(BaseModel):
    transition_index: int
    coherence_result: str
    passes: bool

class Character(BaseModel):
    name: str
    description: str

class StoryMetadata(BaseModel):
    setting: str
    genre: str
    style: str
    characters: List[Character]

class MetadataEvaluation(BaseModel):
    beat_index: int
    metadata_similarity: float
    metadata_evaluation: str
    passes: bool

class GenerationResult(BaseModel):
    final_story: str
    beat_evaluations: List[BeatEvaluation]
    coherence_evaluations: Optional[List[CoherenceEvaluation]] = None
    metadata_evaluations: Optional[List[MetadataEvaluation]] = None

# Request model for /generate endpoint.
class GenerationRequest(BaseModel):
    beats: List[str]
    memory_strategy: Optional[str] = "full"  # Options: "full", "summary", "none"
    enable_coherence_eval: Optional[bool] = False
    temperature: Optional[float] = 0.85
    metadata: Optional[StoryMetadata] = None
    metadata_threshold: Optional[float] = 0.7