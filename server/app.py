# server/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random
from fastapi import Body

app = FastAPI(title="Contract Review Environment", version="1.0.0")

# ── Data ──────────────────────────────────────────────────────────────────────

CONTRACTS = {
    "easy": [
        {"clause": "Payment shall be made within 30 days.", "label": "safe"},
        {"clause": "Either party may terminate with 30-day notice.", "label": "safe"},
        {"clause": "All disputes resolved by binding arbitration with no appeals.", "label": "risky"},
    ],
    "medium": [
        {"clause": "Vendor retains all intellectual property created under this contract.", "label": "risky"},
        {"clause": "Liability is limited to the total contract value.", "label": "safe"},
        {"clause": "Client data may be shared with third parties without notice.", "label": "risky"},
        {"clause": "Automatic renewal unless cancelled 90 days in advance.", "label": "risky"},
    ],
    "hard": [
        {"clause": "Indemnification extends to all affiliates, successors, and assigns in perpetuity.", "label": "risky"},
        {"clause": "Governing law shall be the jurisdiction of the service provider.", "label": "risky"},
        {"clause": "Force majeure excludes pandemics and government actions.", "label": "risky"},
        {"clause": "Confidentiality obligations survive termination for 10 years.", "label": "safe"},
        {"clause": "Liquidated damages of 200% of contract value for early exit.", "label": "risky"},
    ],
}

VALID_ACTIONS = ["mark_safe", "mark_risky", "skip", "suggest_edit"]

# ── State ─────────────────────────────────────────────────────────────────────

class EnvState:
    def __init__(self):
        self.task_level: str = "easy"
        self.contract: List[Dict] = []
        self.current_index: int = 0
        self.done: bool = True
        self.history: List[Dict] = []
        self.total_reward: float = 0.0
        self.step_count: int = 0

_state = EnvState()

# ── Schemas ───────────────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task: Optional[str] = "easy"
    seed: Optional[int] = None

class StepRequest(BaseModel):
    action: str

class Observation(BaseModel):
    clause: str
    clause_index: int
    total_clauses: int
    task: str

class StepResponse(BaseModel):
    observation: Optional[Observation]
    reward: float
    done: bool
    info: Dict[str, Any]

class StateResponse(BaseModel):
    task: str
    current_index: int
    total_clauses: int
    done: bool
    total_reward: float
    step_count: int
    history: List[Dict]

# ── Grader ────────────────────────────────────────────────────────────────────

def grade_action(action: str, label: str) -> float:
    """Returns score in [0.0, 1.0]."""
    if action == "skip":
        return 0.3
    if action == "suggest_edit":
        return 0.5
    if action == "mark_risky" and label == "risky":
        return 1.0
    if action == "mark_safe" and label == "safe":
        return 1.0
    # Wrong classification
    return 0.0

# ── Endpoints ─────────────────────────────────────────────────────────────────



@app.post("/reset", response_model=Observation)
def reset(req: ResetRequest = Body(default=ResetRequest())):
    global _state
    task = req.task if req.task in CONTRACTS else "easy"
    if req.seed is not None:
        random.seed(req.seed)
    _state.task_level = task
    _state.contract = list(CONTRACTS[task])
    random.shuffle(_state.contract)
    _state.current_index = 0
    _state.done = False
    _state.history = []
    _state.total_reward = 0.0
    _state.step_count = 0

    clause = _state.contract[0]
    return Observation(
        clause=clause["clause"],
        clause_index=0,
        total_clauses=len(_state.contract),
        task=task,
    )


@app.post("/step", response_model=StepResponse)
def step(req: StepRequest):
    global _state
    if _state.done:
        raise HTTPException(status_code=400, detail="Episode is done. Call /reset first.")
    if req.action not in VALID_ACTIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid action '{req.action}'. Valid: {VALID_ACTIONS}",
        )

    clause = _state.contract[_state.current_index]
    reward = grade_action(req.action, clause["label"])
    _state.total_reward += reward
    _state.step_count += 1
    _state.history.append({
        "clause": clause["clause"],
        "label": clause["label"],
        "action": req.action,
        "reward": reward,
    })

    _state.current_index += 1
    done = _state.current_index >= len(_state.contract)
    _state.done = done

    next_obs = None
    if not done:
        next_clause = _state.contract[_state.current_index]
        next_obs = Observation(
            clause=next_clause["clause"],
            clause_index=_state.current_index,
            total_clauses=len(_state.contract),
            task=_state.task_level,
        )

    final_score = (
        round(_state.total_reward / len(_state.contract), 4) if done else None
    )

    return StepResponse(
        observation=next_obs,
        reward=round(reward, 4),
        done=done,
        info={
            "clause_index": _state.current_index - 1,
            "correct_label": clause["label"],
            "final_score": final_score,
        },
    )


@app.get("/state", response_model=StateResponse)
def state():
    return StateResponse(
        task=_state.task_level,
        current_index=_state.current_index,
        total_clauses=len(_state.contract),
        done=_state.done,
        total_reward=round(_state.total_reward, 4),
        step_count=_state.step_count,
        history=_state.history,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {"id": "easy", "description": "3 clauses, clear safe/risky labels"},
            {"id": "medium", "description": "4 clauses, moderate ambiguity"},
            {"id": "hard", "description": "5 clauses, complex legal language"},
        ]
    }


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
