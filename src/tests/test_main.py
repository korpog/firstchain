# tests/test_main.py
from unittest.mock import patch
from fastapi import status
from app.db import User, Message, Conversation
import pytest

def test_list_conversations_empty(authenticated_client):
    response = authenticated_client.get("/user/me/conversations/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_list_conversations(authenticated_client, session, test_user):
    conversation = Conversation(user_id=test_user.id)
    session.add(conversation)
    session.commit()
    
    response = authenticated_client.get("/user/me/conversations/")
    assert response.status_code == status.HTTP_200_OK
    conversations = response.json()
    assert len(conversations) == 1
    assert conversations[0]["user_id"] == test_user.id

def test_get_conversation_messages(authenticated_client, session, test_user):
    conversation = Conversation(user_id=test_user.id)
    session.add(conversation)
    session.commit()
    
    message = Message(
        user_id=test_user.id,
        conversation_id=conversation.id,
        message="Test message",
        is_human_message=True
    )
    session.add(message)
    session.commit()
    
    response = authenticated_client.get(f"/conversation/{conversation.id}/messages/")
    assert response.status_code == status.HTTP_200_OK
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["message"] == "Test message"

@patch("main.state_graph")
def test_ask_question(mock_state_graph, authenticated_client, session, test_user):
    mock_state_graph.invoke.return_value = {
        "question": "test question",
        "context": ["test context"],
        "answer": "test answer"
    }
    
    response = authenticated_client.post(
        "/ask/",
        json={"question": "test question"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["answer"] == "test answer"
    
    # Verify messages were stored
    messages = session.query(Message).all()
    assert len(messages) == 2  # Question and answer
    assert messages[0].message == "test question"
    assert messages[1].message == "test answer"