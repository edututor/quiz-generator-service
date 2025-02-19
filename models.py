from sqlalchemy import Column, Integer, String, Boolean, DateTime, text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class QuizModel(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=False)
    document_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))

    # One-to-many relationship: a quiz can have multiple questions
    questions = relationship("QuizQuestionsModel", back_populates="quiz", cascade="all, delete-orphan")
    

class QuizQuestionsModel(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    # ForeignKey to reference the Quiz it belongs to
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(String, nullable=False, unique=False)
    hint = Column(String, nullable=False, unique=False)

    # Relationship back to the Quiz
    quiz = relationship("QuizModel", back_populates="questions")

    # One-to-many relationship: a question can have multiple answers
    answers = relationship("AnswersModel", back_populates="question", cascade="all, delete-orphan")


class AnswersModel(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    # ForeignKey to reference the question it belongs to
    question_id = Column(Integer, ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False)
    answer_text = Column(String, nullable=False, unique=False)
    is_correct_answer = Column(Boolean, nullable=False, unique=False)

    # Relationship back to the QuizQuestions
    question = relationship("QuizQuestionsModel", back_populates="answers")

