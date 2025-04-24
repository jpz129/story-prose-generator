# app/utils/text_utils.py
import spacy

# Load spaCy model once (on module import)
nlp = spacy.load("en_core_web_md")

def word_count(text: str) -> int:
    """Count the number of words in the text."""
    try:
        if not isinstance(text, str):
            raise TypeError("Input text must be a string")
        return len(text.split())
    except Exception as e:
        print(f"Error in word_count: {e}")
        return 0

def beat_coverage_evaluation(beat: str, generated: str) -> float:
    """Compute semantic similarity between beat and generated prose using spaCy."""
    try:
        if not isinstance(beat, str) or not isinstance(generated, str):
            raise TypeError("Both beat and generated must be strings")
        doc_beat = nlp(beat)
        doc_generated = nlp(generated)
        return doc_beat.similarity(doc_generated)
    except Exception as e:
        print(f"Error in beat_coverage_evaluation: {e}")
        return 0.0

def create_metadata_string(metadata: dict) -> str:
    """Flatten metadata dictionary into a string for comparisons."""
    try:
        characters = metadata.get("characters", [])
        characters_str = ", ".join([f"{c['name']}: {c['description']}" for c in characters])
        return f"Genre: {metadata.get('genre')}. Setting: {metadata.get('setting')}. Characters: {characters_str}. Prose Style: {metadata.get('style')}."
    except Exception as e:
        print(f"Error in create_metadata_string: {e}")
        return "Metadata unavailable due to an error."