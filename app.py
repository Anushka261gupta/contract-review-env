from fastapi import FastAPI
from env import ContractEnv
from tasks import TASKS
from grader import evaluate_episode
import random
from pydantic import BaseModel
from typing import List

app = FastAPI()

env = ContractEnv()

# ---------------- ROOT ----------------
@app.get("/")
def home():
    return {
        "message": "Contract Review AI Environment is running!",
        "docs": "/docs"
    }

# ---------------- TASKS ----------------
@app.get("/tasks")
def get_tasks():
    return TASKS

# ---------------- RESET ----------------
@app.post("/reset")
def reset_env():
    obs = env.reset()
    return {"observation": obs}

# ---------------- STEP ----------------
class ActionInput(BaseModel):
    action: str

@app.post("/step")
def step_env(input: ActionInput):
    obs, reward, done, _ = env.step(input.action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done
    }

# ---------------- STATE ----------------
@app.get("/state")
def get_state():
    return {
        "current_index": env.current_index,
        "total_clauses": len(env.current_contract) if env.current_contract else 0
    }

# ---------------- BASELINE ----------------
@app.get("/baseline")
def run_baseline():
    obs = env.reset()
    done = False

    actions = []
    ground_truth = []

    while not done:
        action = random.choice(env.actions)
        clause = env.current_contract[env.current_index]

        ground_truth.append(clause["label"])
        actions.append(action)

        obs, reward, done, _ = env.step(action)

    score = evaluate_episode(actions, ground_truth)

    return {
        "actions": actions,
        "ground_truth": ground_truth,
        "score": score
    }

# ---------------- GRADER ----------------
class GradeRequest(BaseModel):
    actions: List[str]
    ground_truth: List[str]

@app.post("/grader")
def grade(request: GradeRequest):
    score = evaluate_episode(request.actions, request.ground_truth)
    return {"score": score}