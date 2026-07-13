from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from api.workflow import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GuardrailsRequest(BaseModel):
    text: str = Field(..., max_length=500)

class RailStatus(BaseModel):
    passed: bool
    message: str
    redacted_text: str | None = None

class ValidationResponse(BaseModel):
    overall_passed: bool
    keyword_rail: RailStatus
    constraint_rail: RailStatus
    leak_rail: RailStatus
    retrieved_context: str | None = None

@app.post("/api/validate", response_model=ValidationResponse)
def validate_input(req: GuardrailsRequest):
    initial_state = {
        "question": req.text,
        "retrieved_context": "",
        "response": "",
        "redacted_response": "",
        "keyword_passed": True,
        "keyword_message": "",
        "constraint_passed": True,
        "constraint_message": "",
        "leak_passed": True,
        "leak_message": "",
        "overall_passed": True,
        "logs": []
    }
    result = graph.invoke(initial_state)
    
    return ValidationResponse(
        overall_passed=result["overall_passed"],
        keyword_rail=RailStatus(
            passed=result["keyword_passed"],
            message=result["keyword_message"]
        ),
        constraint_rail=RailStatus(
            passed=result["constraint_passed"],
            message=result["constraint_message"]
        ),
        leak_rail=RailStatus(
            passed=result["leak_passed"],
            message=result["leak_message"],
            redacted_text=result["redacted_response"] if result["overall_passed"] else result["response"]
        ),
        retrieved_context=result["retrieved_context"]
    )
