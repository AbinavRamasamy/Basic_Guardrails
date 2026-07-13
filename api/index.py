import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

# Enable CORS for frontend requests
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

BANNED_KEYWORDS = ["admin", "root", "sudo", "hack", "override"]
CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

def validate_keywords(text: str) -> RailStatus:
    text_lower = text.lower()
    for word in BANNED_KEYWORDS:
        if word in text_lower:
            return RailStatus(
                passed=False,
                message=f"Banned keyword '{word}' detected."
            )
    return RailStatus(passed=True, message="No banned keywords detected.")

def validate_constraints(text: str) -> RailStatus:
    if len(text) > 100:
        return RailStatus(
            passed=False,
            message="Input exceeds 100 characters constraint."
        )
    for char in ['[', ']', '<', '>']:
        if char in text:
            return RailStatus(
                passed=False,
                message=f"Forbidden character '{char}' detected."
            )
    return RailStatus(passed=True, message="Input constraints satisfied.")

def validate_leaks(text: str) -> RailStatus:
    redacted = text
    leaks_found = []
    
    # Check SSN
    if SSN_REGEX.search(text):
        leaks_found.append("SSN pattern")
        redacted = SSN_REGEX.sub("[REDACTED SSN]", redacted)
        
    # Check Credit Card
    if CREDIT_CARD_REGEX.search(text):
        leaks_found.append("Credit Card pattern")
        redacted = CREDIT_CARD_REGEX.sub("[REDACTED CC]", redacted)
        
    if leaks_found:
        return RailStatus(
            passed=False,
            message=f"Sensitive leak detected: {', '.join(leaks_found)}.",
            redacted_text=redacted
        )
    return RailStatus(passed=True, message="No sensitive leaks detected.", redacted_text=text)

@app.post("/api/validate", response_model=ValidationResponse)
def validate_input(req: GuardrailsRequest):
    k_status = validate_keywords(req.text)
    c_status = validate_constraints(req.text)
    l_status = validate_leaks(req.text)
    
    overall = k_status.passed and c_status.passed and l_status.passed
    return ValidationResponse(
        overall_passed=overall,
        keyword_rail=k_status,
        constraint_rail=c_status,
        leak_rail=l_status
    )
