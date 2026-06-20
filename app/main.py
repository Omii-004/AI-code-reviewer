from fastapi import FastAPI
from pydantic import BaseModel
from app.routes.review import router as review_router
from app.api.webhook import router as webhook_router

app = FastAPI()

class CodeRequest(BaseModel):
    code: str

app.include_router(webhook_router)

@app.get("/")
def home():
    return {"message": "AI Code Reviewer Running"}

app.include_router(review_router)

@app.post("/review")
def review_code(request: CodeRequest):
    code = request.code

    return {
        "analysis": "Code received successfully",
        "length": len(code)
    }
