from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Chat Service")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Healthcare Chat Service"}

@app.post("/chat/", response_model=schemas.ChatResponse)
async def create_chat_message(chat: schemas.ChatCreate, db: Session = Depends(get_db)):
    # Store the user message
    db_message = models.ChatMessage(
        user_id=chat.user_id,
        message=chat.message,
        is_user=True
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    # Generate AI response
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful healthcare assistant."},
                {"role": "user", "content": chat.message}
            ]
        )
        ai_response = response.choices[0].message.content

        # Store the AI response
        db_ai_message = models.ChatMessage(
            user_id=chat.user_id,
            message=ai_response,
            is_user=False
        )
        db.add(db_ai_message)
        db.commit()
        db.refresh(db_ai_message)

        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{user_id}", response_model=List[schemas.ChatMessage])
def read_chat_history(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage)\
        .filter(models.ChatMessage.user_id == user_id)\
        .order_by(models.ChatMessage.created_at)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return messages 