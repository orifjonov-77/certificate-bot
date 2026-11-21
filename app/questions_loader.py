import json
import os
from typing import Dict, List, Any
from app.config import QUESTIONS_PATH

_cached_questions: Dict[str, Any] = {}

def load_questions() -> Dict[str, Any]:
    global _cached_questions
    if not _cached_questions:
        if not os.path.exists(QUESTIONS_PATH):
            raise FileNotFoundError(f"Questions file not found: {QUESTIONS_PATH}")
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
            _cached_questions = json.load(f)
    return _cached_questions

def get_directions() -> List[Dict[str, str]]:
    data = load_questions()
    directions = []
    for key, val in data.items():
        directions.append({
            "id": key,
            "title": val.get("title", key)
        })
    return directions

def get_questions_for_direction(direction_id: str) -> List[Dict[str, Any]]:
    data = load_questions()
    if direction_id in data:
        return data[direction_id].get("questions", [])
    return []

def get_direction_title(direction_id: str) -> str:
    data = load_questions()
    if direction_id in data:
        return data[direction_id].get("title", direction_id)
    return direction_id

def save_all_questions(data: Dict[str, Any]):
    global _cached_questions
    _cached_questions = data
    with open(QUESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_or_update_question(direction_id: str, question_id: int, question_text: str, options: Dict[str, str], answer: str):
    data = load_questions()
    if direction_id not in data:
        return False
    questions = data[direction_id].setdefault("questions", [])
    found = False
    for i, q in enumerate(questions):
        if q["id"] == question_id:
            questions[i] = {
                "id": question_id,
                "question": question_text,
                "options": options,
                "answer": answer.upper()
            }
            found = True
            break
    if not found:
        new_id = len(questions) + 1 if not question_id else question_id
        questions.append({
            "id": new_id,
            "question": question_text,
            "options": options,
            "answer": answer.upper()
        })
    save_all_questions(data)
    return True

def delete_question(direction_id: str, question_id: int):
    data = load_questions()
    if direction_id not in data:
        return False
    questions = data[direction_id].get("questions", [])
    initial_len = len(questions)
    questions = [q for q in questions if q["id"] != question_id]
    # ID larni qayta tartiblash (1..N)
    for idx, q in enumerate(questions, 1):
        q["id"] = idx
    data[direction_id]["questions"] = questions
    save_all_questions(data)
    return len(questions) < initial_len

