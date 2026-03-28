from fastapi import FastAPI
from env import ContractEnv
from tasks import TASKS
from grader import evaluate_episode
import random
from pydantic import BaseModel
from typing import List

app = FastAPI()

env = ContractEnv()

#  TASKS API

@app.get("/")
def home():
    return {"message": "Contract Review AI Environment is running!"}


@app.get("/tasks")
def get_tasks():
    return TASKS


#  BASELINE API
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


#  GRADER API

class GradeRequest(BaseModel):
    actions: List[str]
    ground_truth: List[str]


@app.post("/grader")
def grade(request: GradeRequest):
    score = evaluate_episode(request.actions, request.ground_truth)
    return {"score": score}