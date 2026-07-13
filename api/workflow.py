import os
import re
from typing import List, TypedDict
from langgraph.graph import StateGraph, START, END

# --- STATE DEFINITION ---

class BasicState(TypedDict):
    question: str
    retrieved_context: str
    response: str
    redacted_response: str
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
    text = state['question'].lower()
    banned = ['admin', 'root', 'sudo', 'hack', 'override']
    triggered = [w for w in banned if w in text]
    
    if triggered:
        state['keyword_passed'] = False
        state['keyword_message'] = f"Query contains prohibited keyword(s): {', '.join(triggered)}"
        state['logs'].append("[check_keywords]: Flagged prohibited keyword usage.")
    else:
        state['keyword_passed'] = True
        state['keyword_message'] = "Pass"
        state['logs'].append("[check_keywords]: Verified keyword safety.")
    return state

def check_constraints(state: BasicState) -> BasicState:
    text = state['question']
    
    if len(text) > 100:
        state['constraint_passed'] = False
        state['constraint_message'] = f"Query length ({len(text)} characters) exceeds the 100 character maximum limit."
        state['logs'].append("[check_constraints]: Flagged length restriction violation.")
        return state
        
    brackets = ['<', '>', '[', ']']
    found = [b for b in brackets if b in text]
    if found:
        state['constraint_passed'] = False
        state['constraint_message'] = f"Query contains restricted special bracket characters: {', '.join(found)}"
        state['logs'].append("[check_constraints]: Flagged injection bracket usage.")
    else:
        state['constraint_passed'] = True
        state['constraint_message'] = "Pass"
        state['logs'].append("[check_constraints]: Verified structural constraints.")
    return state

def retrieve_context(state: BasicState) -> BasicState:
    # If prior nodes flagged as unsafe, skip retrieval
    if not state['keyword_passed'] or not state['constraint_passed']:
        state['retrieved_context'] = ""
        return state
        
    # Resolve paths relative to this file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tasks_path = os.path.join(base_dir, "data", "tasks.txt")
    policies_path = os.path.join(base_dir, "data", "policies.txt")
    
    all_lines = []
    try:
        if os.path.exists(tasks_path):
            with open(tasks_path, "r") as f:
                all_lines.extend(f.readlines())
        if os.path.exists(policies_path):
            with open(policies_path, "r") as f:
                all_lines.extend(f.readlines())
    except Exception as e:
        state['logs'].append(f"[retrieve_context]: Error loading source files: {e}")
        
    # Clean up lines
    all_lines = [line.strip() for line in all_lines if line.strip()]
    
    # Simple word-matching retrieval
    query_words = re.findall(r"\b\w{3,}\b", state['question'].lower())
    stop_words = {'the', 'and', 'for', 'you', 'are', 'with', 'from', 'what', 'who', 'how', 'list', 'show', 'find'}
    search_terms = [w for w in query_words if w not in stop_words]
    
    matching_lines = []
    for line in all_lines:
        line_lower = line.lower()
        if any(term in line_lower for term in search_terms):
            matching_lines.append(line)
            
    # Fallback to returning everything if query is generic
    if not matching_lines and ("all" in state['question'].lower() or "show" in state['question'].lower()):
        matching_lines = all_lines
        
    state['retrieved_context'] = "\n".join(matching_lines)
    state['logs'].append(f"[retrieve_context]: Retrieved {len(matching_lines)} relevant lines from local text files.")
    return state

def generate_response(state: BasicState) -> BasicState:
    if not state['keyword_passed'] or not state['constraint_passed']:
        state['response'] = ""
        return state
        
    context = state['retrieved_context']
    if not context:
        state['response'] = "No matching records found in local task or policy files."
    else:
        state['response'] = f"Found local reference files matching your query:\n\n{context}"
        
    state['logs'].append("[generate_response]: Generated local report from retrieved chunks.")
    return state

def check_leaks(state: BasicState) -> BasicState:
    if not state['keyword_passed'] or not state['constraint_passed']:
        state['redacted_response'] = ""
        return state
        
    text = state['response']
    
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    
    has_ssn = bool(re.search(ssn_pattern, text))
    has_cc = bool(re.search(cc_pattern, text))
    
    redacted = text
    redacted = re.sub(ssn_pattern, "[SSN REDACTED]", redacted)
    redacted = re.sub(cc_pattern, "[CREDIT CARD REDACTED]", redacted)
    
    state['redacted_response'] = redacted
    
    if has_ssn or has_cc:
        state['leak_passed'] = False
        state['leak_message'] = f"Sensitive leaks redacted: {'SSN' if has_ssn else ''} {'Credit Card' if has_cc else ''}".strip()
        state['logs'].append("[check_leaks]: Redacted sensitive credential pattern matched in context.")
    else:
        state['leak_passed'] = True
        state['leak_message'] = "Pass"
        state['logs'].append("[check_leaks]: Verified output context safety.")
    return state

def evaluate_overall(state: BasicState) -> BasicState:
    passed = state['keyword_passed'] and state['constraint_passed']
    state['overall_passed'] = passed
    state['logs'].append(f"[evaluate_overall]: Evaluation finished with status: {'PASSED' if passed else 'BLOCKED'}")
    return state

# --- ROUTING FUNCTIONS ---

def route_after_plan(state: BasicState) -> str:
    if not state['keyword_passed'] or not state['constraint_passed']:
        return 'blocked'
    return 'safe'

# --- COMPILE STATE GRAPH ---

builder = StateGraph(BasicState)
builder.add_node("keywords", check_keywords)
builder.add_node("constraints", check_constraints)
builder.add_node("retrieve", retrieve_context)
builder.add_node("generate", generate_response)
builder.add_node("leaks", check_leaks)
builder.add_node("evaluate", evaluate_overall)

builder.add_edge(START, "keywords")
builder.add_edge("keywords", "constraints")
builder.add_conditional_edges("constraints", route_after_plan, {
    "safe": "retrieve",
    "blocked": END
})
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "leaks")
builder.add_edge("leaks", "evaluate")
builder.add_edge("evaluate", END)

graph = builder.compile()
