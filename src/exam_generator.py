"""
Mini exam generation and local solution grading.
"""

from typing import Optional
import json

import ollama

from config import DEFAULT_MODEL, MAX_TOKENS, TEMPERATURE, OLLAMA_HOST, OLLAMA_VISION_MODEL
from src.ai_provider import AIProvider
from src.json_utils import extract_json


class ExamGenerator:
    """Generate exam-style tasks and grade submitted solutions."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "ollama", model: str = None):
        self.provider = AIProvider(
            provider_type=provider,
            api_key=api_key,
            model=model or DEFAULT_MODEL
        )
        self.model = model or DEFAULT_MODEL
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE

    def generate_exam(self, transcription: str, language: str = None, num_tasks: int = 5, difficulty: str = "medium to hard") -> list:
        language_instruction = language or "the same language as the lecture transcription"
        prompt = f"""Create a {difficulty} mini exam in {language_instruction} from the lecture.
Return only valid JSON, no markdown. The JSON must be an array with {num_tasks} items.
Each item must have:
- title: short task title
- difficulty: the task difficulty
- prompt: the full task students must solve
- expected_answer: model answer or grading rubric
- points: integer from 5 to 20
Make the tasks realistic for a course test, not just simple recall.
Create fresh tasks that differ from a previous attempt."""

        response = self.provider.chat_completion(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcription}
            ],
            max_tokens=self.max_tokens * 2,
            temperature=self.temperature
        )
        return extract_json(response)


class LocalSolutionGrader:
    """Grade text or image solutions with local Ollama models."""

    def __init__(self, text_model: str = None, vision_model: str = None):
        self.text_client = ollama.Client(host=OLLAMA_HOST)
        self.text_model = text_model or DEFAULT_MODEL
        self.vision_model = vision_model or OLLAMA_VISION_MODEL

    def grade_text(self, exam_tasks: list, solution_text: str, language: str = None) -> str:
        language_instruction = language or "the same language as the exam"
        prompt = _grading_prompt(exam_tasks, language_instruction)
        response = self.text_client.chat(
            model=self.text_model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": solution_text}
            ],
            options={"temperature": 0.2, "num_predict": 1600},
        )
        return response["message"]["content"]

    def grade_image(self, exam_tasks: list, image_path: str, language: str = None) -> str:
        language_instruction = language or "the same language as the exam"
        prompt = _grading_prompt(exam_tasks, language_instruction)
        response = self.text_client.chat(
            model=self.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\nRead the submitted solution from this image and grade it.",
                    "images": [image_path],
                }
            ],
            options={"temperature": 0.2, "num_predict": 1800},
        )
        return response["message"]["content"]


def _grading_prompt(exam_tasks: list, language_instruction: str) -> str:
    return f"""You are a strict but helpful teacher. Grade the student's submitted solution in {language_instruction}.
Use these exam tasks and rubrics:
{json.dumps(exam_tasks, ensure_ascii=False, indent=2)}

Return:
1. total score and maximum score
2. score for each task
3. what is correct
4. what is missing or wrong
5. the correct answer or solution outline"""
