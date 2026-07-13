import re
from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END

# --- LANGGRAPH GRAPH STATE ---

class BasicState(TypedDict):
    text: str
    redacted_text: str
    keyword_passed: bool
    keyword_message: str
    constraint_passed: bool
    constraint_message: str
    leak_passed: bool
    leak_message: str
    overall_passed: bool
    logs: List[str]

# --- NODE FUNCTIONS ---

def check_keywords(state: BasicState) -> BasicState:
    text = state['text'].lower()
    banned = ['admin', 'root', 'sudo', 'hack', 'override']
    triggered = [w for w in banned if w in text]
    
    if triggered:
        state['keyword_passed'] = False
        state['keyword_message'] = f"Input contains prohibited keyword(s): {', '.join(triggered)}"
        state['logs'].append("[check_keywords]: Flagged prohibited keyword usage.")
    else:
        state['keyword_passed'] = True
        state['keyword_message'] = "Pass"
        state['logs'].append("[check_keywords]: Verified keyword safety.")
    return state

def check_constraints(state: BasicState) -> BasicState:
    text = state['text']
    
    if len(text) > 100:
        state['constraint_passed'] = False
        state['constraint_message'] = f"Input length ({len(text)} characters) exceeds the 100 character maximum limit."
        state['logs'].append("[check_constraints]: Flagged length restriction violation.")
        return state
        
    brackets = ['<', '>', '[', ']']
    found = [b for b in brackets if b in text]
    if found:
        state['constraint_passed'] = False
        state['constraint_message'] = f"Input contains restricted special bracket characters: {', '.join(found)}"
        state['logs'].append("[check_constraints]: Flagged injection bracket usage.")
    else:
        state['constraint_passed'] = True
        state['constraint_message'] = "Pass"
        state['logs'].append("[check_constraints]: Verified structural constraints.")
    return state

def check_leaks(state: BasicState) -> BasicState:
    text = state['text']
    
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    
    has_ssn = bool(re.search(ssn_pattern, text))
    has_cc = bool(re.search(cc_pattern, text))
    
    redacted = text
    redacted = re.sub(ssn_pattern, "[SSN REDACTED]", redacted)
    redacted = re.sub(cc_pattern, "[CREDIT CARD REDACTED]", redacted)
    
    state['redacted_text'] = redacted
    
    if has_ssn or has_cc:
        state['leak_passed'] = False
        state['leak_message'] = f"Sensitive leaks redacted: {'SSN' if has_ssn else ''} {'Credit Card' if has_cc else ''}".strip()
        state['logs'].append("[check_leaks]: Redacted sensitive credential pattern match.")
    else:
        state['leak_passed'] = True
        state['leak_message'] = "Pass"
        state['logs'].append("[check_leaks]: Verified credential safety.")
    return state

def evaluate_overall(state: BasicState) -> BasicState:
    passed = state['keyword_passed'] and state['constraint_passed'] and state['leak_passed']
    state['overall_passed'] = passed
    state['logs'].append(f"[evaluate_overall]: Evaluation finished with status: {'PASSED' if passed else 'BLOCKED'}")
    return state

# --- COMPILE STATE GRAPH ---

builder = StateGraph(BasicState)
builder.add_node("keywords", check_keywords)
builder.add_node("constraints", check_constraints)
builder.add_node("leaks", check_leaks)
builder.add_node("evaluate", evaluate_overall)

builder.add_edge(START, "keywords")
builder.add_edge("keywords", "constraints")
builder.add_edge("constraints", "leaks")
builder.add_edge("leaks", "evaluate")
builder.add_edge("evaluate", END)

graph = builder.compile()
