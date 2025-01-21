from datetime import datetime, timezone
from typing import Annotated, Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, Relationship, create_engine, select

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str = Field()
    messages: list["Message"] = Relationship(back_populates="user")
    conversations: list["Conversation"] = Relationship(back_populates="user")

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    conversation_id: int = Field(foreign_key="conversation.id")
    user: User = Relationship(back_populates="messages")
    conversation: "Conversation" = Relationship(back_populates="messages")
    message: str = Field(min_length=1, max_length=1000)    
    is_human_message: bool = Field(default=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="conversations")
    messages: list[Message] = Relationship(back_populates="conversation")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]