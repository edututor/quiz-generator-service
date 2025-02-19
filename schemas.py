from pydantic import BaseModel
from typing import List

# Analysis generation
class Answers(BaseModel):
    answer: str
    is_correct_answer: bool

# Report generation
class Question(BaseModel):
    question_text: str
    answers: List[Answers]
    hint: str

class QuizSchema(BaseModel):
    quiz_name: str
    questions: List[Question]

class QuizRequest(BaseModel):
    document_name: str
    user_query: str
