# app/services/story_generator_service.py
from typing import List, Optional, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from app.core.config import ANTHROPIC_KEY
from app.models.generation import BeatEvaluation, CoherenceEvaluation, MetadataEvaluation, GenerationResult
from app.utils.text_utils import word_count, beat_coverage_evaluation, create_metadata_string
import spacy

# Initialize spaCy model (reuse same instance as in text_utils if desired)
nlp = spacy.load("en_core_web_md")

def evaluate_coherence(previous_text: str, current_text: str, llm: ChatAnthropic) -> Any:
    prompt_template = PromptTemplate(
        input_variables=["previous_text", "current_text"],
        template="""
Evaluate the coherence between the following two paragraphs.
Paragraph 1: "{previous_text}"
Paragraph 2: "{current_text}"
Is the transition between these paragraphs coherent? Answer only "Good" or "Needs Improvement" followed by a brief explanation.
"""
    )
    chain = prompt_template | llm
    return chain.invoke({"previous_text": previous_text, "current_text": current_text})

def summarize_context(context: str, llm: ChatAnthropic) -> str:
    summary_prompt = PromptTemplate(
        input_variables=["context"],
        template="""
You are a summarization expert. Please provide a concise summary of the following text:

Context:
"{context}"

Summary:
"""
    )
    summary_chain = summary_prompt | llm
    summary_result = summary_chain.invoke({"context": context})
    return summary_result.content

def evaluate_metadata_adherence(prose: str, metadata: dict, llm: ChatAnthropic, threshold: float = 0.7) -> Dict[str, Any]:
    from app.utils.text_utils import create_metadata_string  # reuse function
    meta_text = create_metadata_string(metadata)
    doc_meta = nlp(meta_text)
    doc_generated = nlp(prose)
    sim = doc_meta.similarity(doc_generated)
    if sim >= threshold:
        return {"result": f"Good (spaCy similarity: {sim:.2f})", "passes": True, "similarity": sim}
    else:
        prompt_template = PromptTemplate(
            input_variables=["metadata", "passage"],
            template="""
Evaluate the following passage for how well it adheres to the given story metadata.

Metadata:
"{metadata}"

Passage:
"{passage}"

Is the passage consistent with the metadata above? Answer only "Good" or "Needs Improvement" with a brief explanation.
"""
        )
        eval_chain = prompt_template | llm
        result = eval_chain.invoke({"metadata": meta_text, "passage": prose})
        result_text = result.content if hasattr(result, "content") else result
        passes = result_text.strip().lower().startswith("good")
        return {"result": result_text, "passes": passes, "similarity": sim}

def generate_prose_from_beats(
    beats: List[str],
    memory_strategy: str = "full",   # "full", "summary", "none"
    enable_coherence_eval: bool = False,
    temperature: float = 0.85,
    metadata: Optional[dict] = None,
    metadata_threshold: float = 0.7
) -> GenerationResult:
    # Initialize the LLM for generating text (using Anthropic's model)
    llm = ChatAnthropic(
        model="claude-3-7-sonnet-latest",
        temperature=temperature,
        anthropic_api_key=ANTHROPIC_KEY,
        max_tokens=225,
    )

    # Define prompt including metadata details if provided.
    prompt_template = PromptTemplate(
        input_variables=["beat", "previous_context", "characters", "setting", "genre", "style"],
        template="""
Previous context:
"{previous_context}"

Story Metadata:
- Genre: {genre}
- Setting: {setting}
- Characters: {characters}
- Prose Style: {style}

You are a novelist tasked with turning story beats into beautifully written prose. Given the current beat and the metadata above, write a vivid, emotionally resonant passage (approximately 125 words) that flows with the previous content.

Current beat:
"{beat}"

Now write the next passage:
"""
    )
    chain = prompt_template | llm

    generated_prose = []
    beat_eval_results = []
    metadata_eval_results = []
    previous_context = ""
    
    # Prepare metadata components (if available)
    if metadata:
        metadata_str = create_metadata_string(metadata)
        setting = metadata.get("setting", "Not specified")
        genre = metadata.get("genre", "Not specified")
        style = metadata.get("style", "Not specified")
        characters = ", ".join([f"{c['name']}: {c['description']}" for c in metadata.get("characters", [])])
    else:
        metadata_str = setting = genre = style = characters = "Not specified"

    for i, beat in enumerate(beats):
        try:
            response = chain.invoke({
                "beat": beat,
                "previous_context": previous_context,
                "characters": characters,
                "setting": setting,
                "genre": genre,
                "style": style
            })
            result = response.content if hasattr(response, "content") else response
        except Exception as e:
            print(f"Error generating prose for beat {i+1}: {e}")
            result = "Error generating prose for this beat."
        generated_prose.append(result)
        count = word_count(result)
        coverage = beat_coverage_evaluation(beat, result)
        length_ok = 100 <= count <= 150
        beat_eval_results.append(BeatEvaluation(
        beat_index=i+1,
        word_count=count,
        length_ok=length_ok,
        beat_coverage_score=coverage
    ))
        # Evaluate metadata adherence if metadata provided.
        if metadata:
            meta_eval = evaluate_metadata_adherence(result, metadata, llm, threshold=metadata_threshold)
            metadata_eval_results.append({
                "beat_index": i+1,
                "metadata_similarity": meta_eval["similarity"],
                "metadata_evaluation": meta_eval["result"],
                "passes": meta_eval["passes"]
            })
        # Update context based on memory strategy.
        if memory_strategy == "full":
            previous_context += "\n\n" + result
        elif memory_strategy == "summary":
            combined_context = previous_context + "\n\n" + result if previous_context else result
            try:
                previous_context = summarize_context(combined_context, llm)
            except Exception as e:
                print(f"Error summarizing context for beat {i+1}: {e}")
                previous_context = combined_context
        elif memory_strategy == "none":
            previous_context = ""

    coherence_eval_results = []
    if enable_coherence_eval and len(generated_prose) > 1:
        for i in range(1, len(generated_prose)):
            try:
                coherence_output = evaluate_coherence(generated_prose[i-1], generated_prose[i], llm)
                coherence_text = coherence_output.content if hasattr(coherence_output, "content") else coherence_output
            except Exception as e:
                print(f"Error evaluating coherence for transition {i}: {e}")
                coherence_text = "Needs Improvement: Error during coherence evaluation."
            passes = coherence_text.strip().lower().startswith("good")
            coherence_eval_results.append({
                "transition_index": i,
                "coherence_result": coherence_text,
                "passes": passes
            })

    full_story = "\n\n".join(generated_prose)
    return GenerationResult(
        final_story=full_story,
        beat_evaluations=beat_eval_results,
        coherence_evaluations=coherence_eval_results if enable_coherence_eval else None,
        metadata_evaluations=metadata_eval_results if metadata else None
    )