from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import ValidationError
from datetime import datetime
from typing import Annotated
from sqlmodel import Session, select
from .llm import setup_llm
from .models import Question, Answer, Document
from .db import User, Conversation, Message, create_db_and_tables, get_session
from .auth import router as auth_router, get_current_user
from fastapi.middleware.cors import CORSMiddleware



# Initialize FastAPI app
app = FastAPI()
app.include_router(auth_router)

origins = [
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

state_graph = setup_llm()


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/user/me/conversations/", response_model=list[Conversation])
def list_conversations(current_user: Annotated[User, Depends(get_current_user)],
                        db: Annotated[Session, Depends(get_session)]) -> list[Conversation]:
    """
    List conversations for the current user.
    Requires authentication.
    """
    statement = db.exec(select(Conversation).where(
        Conversation.user_id == current_user.id).order_by(Conversation.timestamp, Conversation.id))
    result = statement.all()
    return result


@app.get("/conversation/{conversation_id}/messages/", response_model=list[Message])
def get_conversation(
    conversation_id: int, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_session)]
) -> list[Message]:
    """
    Get messages from a conversation.
    Requires authentication.
    """
    statement = db.exec(select(Message).where(
        Message.conversation_id == conversation_id).order_by(Message.timestamp, Message.id))
    result = statement.all()
    return result


@app.post("/ask/")
def ask_question(
    request: Question,
    current_user: Annotated[User, Depends(get_current_user)], 
    db: Annotated[Session, Depends(get_session)]
) -> Answer:
    """
    Ask a question and get an answer.
    Either creates a new conversation or adds to an existing one.
    Requires authentication.
    """
    statement = db.exec(select(Conversation).where(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.timestamp.desc()))
    latest_conversation = statement.first()
    
    if not latest_conversation:
        conversation = Conversation(user_id=current_user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    else:
        conversation = latest_conversation
    
    response = state_graph.invoke({"question": request.question})
    
    if not response or "answer" not in response:
        raise HTTPException(
            status_code=500,
            detail="Invalid response from processing pipeline"
        )
    
    question_message = Message(
        user_id=current_user.id,
        conversation_id=conversation.id,
        message=request.question,
        is_human_message=True
    )
    db.add(question_message)
    
    answer_message = Message(
        user_id=current_user.id,
        conversation_id=conversation.id,
        message=response["answer"],
        is_human_message=False
    )
    db.add(answer_message)
    db.commit()
    
    return Answer(
        question=response["question"],
        context=response["context"],
        answer=response["answer"]
    )