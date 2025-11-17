"""
Database Schemas for IMAGINE game

Each Pydantic model represents a collection in MongoDB. Collection name is the lowercase of the class name.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Mode(BaseModel):
    key: str = Field(..., description="Unique key for the mode: child, arts, creative, technology")
    title: str = Field(..., description="Display title for the mode")
    description: str = Field(..., description="Short description of the mode")
    color: str = Field(..., description="Primary color for the mode UI")

class Question(BaseModel):
    mode: str = Field(..., description="Mode key this question belongs to")
    text: str = Field(..., description="The creative prompt/question text")
    tags: Optional[List[str]] = Field(default=None, description="Related tags")
    locale: str = Field("en-KE", description="Locale of the prompt")

class Answer(BaseModel):
    mode: str = Field(..., description="Mode key")
    question_text: str = Field(..., description="The question being answered")
    answer_text: str = Field(..., description="User's answer/idea")
    username: Optional[str] = Field(default=None, description="Optional player name")
    points_awarded: int = Field(0, description="Gamified points awarded for the idea")

class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: str
    content: str
    image: Optional[str] = None
    author: str = Field("IMAGINE Team")
    published_at: datetime = Field(default_factory=datetime.utcnow)

class ContactMessage(BaseModel):
    name: str
    email: str
    subject: str
    message: str

class ChatMessage(BaseModel):
    username: str
    text: str
    mode: Optional[str] = Field(default=None, description="Optional mode context for the chat message")

class PricingPlan(BaseModel):
    name: str
    price_month: float
    price_year: float
    features: List[str]
