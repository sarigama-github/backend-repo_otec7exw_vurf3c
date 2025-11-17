import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document, get_documents, db
from schemas import Mode, Question, Answer, BlogPost, ContactMessage, ChatMessage, PricingPlan

app = FastAPI(title="IMAGINE API", description="Creative world-building card game for Kenya")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "IMAGINE API running"}

# Utility to seed default content (modes, pricing)
@app.post("/seed")
def seed_content():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    existing = db["mode"].count_documents({})
    if existing == 0:
        default_modes = [
            Mode(key="child", title="Child", description="Playful prompts for kids to imagine better worlds.", color="#FDBA74"),
            Mode(key="arts", title="Arts & Culture", description="Explore culture, identity and expression.", color="#FDE68A"),
            Mode(key="creative", title="Creative", description="Open-ended ideation and storytelling.", color="#86EFAC"),
            Mode(key="technology", title="Technology", description="Invent systems and tools for the future.", color="#93C5FD"),
        ]
        for m in default_modes:
            create_document("mode", m)

    existing_pricing = db["pricingplan"].count_documents({})
    if existing_pricing == 0:
        plans = [
            PricingPlan(name="Starter", price_month=0, price_year=0, features=["Community play", "Basic prompts", "Public chat"]),
            PricingPlan(name="Creator", price_month=4.99, price_year=49.0, features=["All modes", "Saved worlds", "Custom decks"]),
            PricingPlan(name="Team", price_month=14.99, price_year=149.0, features=["Facilitator tools", "Scoreboards", "Workshop mode"]),
        ]
        for p in plans:
            create_document("pricingplan", p)

    return {"status": "seeded"}

# Questions
@app.get("/questions", response_model=List[Question])
def list_questions(mode: Optional[str] = None, limit: int = 50):
    filt = {"mode": mode} if mode else {}
    docs = get_documents("question", filt, limit)
    return [Question(**{k: v for k, v in d.items() if k in Question.model_fields}) for d in docs]

class NewQuestion(BaseModel):
    mode: str
    text: str
    tags: Optional[List[str]] = None
    locale: str = "en-KE"

@app.post("/questions")
def create_question(payload: NewQuestion):
    if payload.mode not in ["child", "arts", "creative", "technology"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    created_id = create_document("question", payload.dict())
    return {"id": created_id}

# Answers
@app.post("/answers")
def submit_answer(ans: Answer):
    created_id = create_document("answer", ans)
    return {"id": created_id}

@app.get("/answers")
def list_answers(mode: Optional[str] = None, limit: int = 50):
    filt = {"mode": mode} if mode else {}
    docs = get_documents("answer", filt, limit)
    return docs

# Modes
@app.get("/modes", response_model=List[Mode])
def get_modes():
    docs = get_documents("mode", {}, 10)
    if not docs:
        # provide defaults without DB write if not seeded
        return [
            Mode(key="child", title="Child", description="Playful prompts for kids to imagine better worlds.", color="#FDBA74"),
            Mode(key="arts", title="Arts & Culture", description="Explore culture, identity and expression.", color="#FDE68A"),
            Mode(key="creative", title="Creative", description="Open-ended ideation and storytelling.", color="#86EFAC"),
            Mode(key="technology", title="Technology", description="Invent systems and tools for the future.", color="#93C5FD"),
        ]
    return [Mode(**{k: v for k, v in d.items() if k in Mode.model_fields}) for d in docs]

# Pricing
@app.get("/pricing", response_model=List[PricingPlan])
def get_pricing():
    docs = get_documents("pricingplan", {}, 10)
    if not docs:
        return [
            PricingPlan(name="Starter", price_month=0, price_year=0, features=["Community play", "Basic prompts", "Public chat"]),
            PricingPlan(name="Creator", price_month=4.99, price_year=49.0, features=["All modes", "Saved worlds", "Custom decks"]),
            PricingPlan(name="Team", price_month=14.99, price_year=149.0, features=["Facilitator tools", "Scoreboards", "Workshop mode"]),
        ]
    return [PricingPlan(**{k: v for k, v in d.items() if k in PricingPlan.model_fields}) for d in docs]

# Blog
@app.get("/blog", response_model=List[BlogPost])
def list_blog():
    docs = get_documents("blogpost", {}, 20)
    return [BlogPost(**{k: v for k, v in d.items() if k in BlogPost.model_fields}) for d in docs]

@app.post("/blog")
def create_blog(post: BlogPost):
    created_id = create_document("blogpost", post)
    return {"id": created_id}

# Contact form
@app.post("/contact")
def contact(message: ContactMessage):
    created_id = create_document("contactmessage", message)
    return {"id": created_id, "status": "received"}

# Chat (simple public stream)
@app.post("/chat")
def send_chat(msg: ChatMessage):
    created_id = create_document("chatmessage", msg)
    return {"id": created_id}

@app.get("/chat")
def get_chat(limit: int = 30):
    docs = get_documents("chatmessage", {}, limit)
    return docs

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
