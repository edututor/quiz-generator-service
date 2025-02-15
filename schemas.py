from pydantic import BaseModel
from typing import List

# Analysis generation
class Answers(BaseModel):
    answer: str
    is_correct_answer: bool

# Report generation
class Question(BaseModel):
    question: str
    answers: List[Answers]
    hint: str

class Quiz(BaseModel):
    quiz_name: str
    questions: List[Question]

