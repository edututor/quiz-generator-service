from loguru import logger
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from agents import quiz_generator_agent, math_tutor_agent
from openai_client import OpenAiClient
from schemas import QuizSchema, Question, Answers, QuizRequest, MathRequest
from vector_manager import VectorManager
from pinecone import Pinecone
from config import settings
from quiz_generator import QuizGenerator
from database import SessionLocal, Base, engine
from models import QuizModel, QuizQuestionsModel, AnswersModel
from sqlalchemy.orm import Session
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        yield db
    finally:
        db.close()


@app.post("/api/generate-quiz")
def main(
    request: QuizRequest,
    db: Session = Depends(get_db)  # <--- Inject DB session here
):
    document_name = request.document_name
    user_query = request.user_query
    try:
        # Initialize required components
        client = OpenAiClient()
        vector_manager = VectorManager()
        pc = Pinecone(api_key=settings.pinecone_api_key)
        quiz_generator = QuizGenerator()

        # Convert to lowercase if desired
        # document_name = document_name.lower()

        # Create embeddings for user query
        logger.info("Creating embeddings for user_query...")
        query_embeddings = vector_manager.vectorize(client, user_query)

        # Access Pinecone indexes
        logger.info("Accessing Pinecone indexes...")
        text_index = pc.Index("document-text-index")

        # Get relevant chunks
        logger.info(f"Getting relevant chunks for: {user_query}")
        chunks = vector_manager.get_chunks(text_index, document_name, query_embeddings)

        # Generate quiz using your custom quiz generator
        logger.info(f"Generating the quiz...")
        quiz_response: QuizSchema = quiz_generator.generate_quiz(
            user_query, 
            chunks, 
            quiz_generator_agent, 
            QuizSchema, 
            client
        )
        logger.info(f"Number of questions: {len(quiz_response.questions)}")

        # Create and save the quiz record
        quiz = QuizModel(
            title=quiz_response.quiz_name,
            document_name=document_name
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        # Create and save each question
        for question in quiz_response.questions:
            question_db = QuizQuestionsModel(
                quiz_id=quiz.id,
                question_text=question.question_text,
                hint=question.hint
            )
            db.add(question_db)
            db.commit()
            db.refresh(question_db)

            # Create and save each answer
            for answer in question.answers:
                answer_db = AnswersModel(
                    question_id=question_db.id,
                    answer_text=answer.answer,
                    is_correct_answer=answer.is_correct_answer
                )
                db.add(answer_db)

            # You can either commit once per question or do one big commit at the end
            db.commit()

        return JSONResponse(
            status_code=200,
            content={"message": "Quiz generated and saved successfully."},
        )

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while processing the request.")


@app.post("/api/math-tutor")
async def math_tutor(request: MathRequest):
    """
    AI Math Tutor that explains concepts and solves problems.

    No need for db injection/session yet as this is just to investigate how useful a math agent could be
    """
    try:
        client = OpenAiClient()

        # Construct AI prompt
        prompt = math_tutor_agent.prompt(f"Math question: {request.question}")
        
        # Query OpenAI API
        response = client.query_gpt(prompt)
        
        return JSONResponse(status_code=200, content={"response": response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Math Tutor API: {str(e)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
