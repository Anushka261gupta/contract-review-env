# inference.py
"""
Inference script: runs an AI agent against the contract review environment.
Uses OpenAI proxy provided by hackathon.
"""

import os
import json
import requests
from openai import OpenAI

BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

VALID_ACTIONS = ["mark_safe", "mark_risky", "skip", "suggest_edit"]


def call_openai(clause: str) -> str:
    try:
        client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("API_BASE_URL"),
        )

        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a contract review expert. "
                        "Given a contract clause, return a JSON with fields: "
                        "'action' and 'suggestion'. "
                        "Action must be one of: mark_safe, mark_risky, skip, suggest_edit. "
                        "If the clause is risky, provide a short suggestion to improve it."
                    ),
                },
                {"role": "user", "content": clause},
            ],
        )

        output = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(output)
            action = parsed.get("action", "skip")
            suggestion = parsed.get("suggestion", "")
        except Exception:
            action = output.lower()
            suggestion = ""

        if action == "mark_risky" and suggestion:
            action = "suggest_edit"

        return action if action in VALID_ACTIONS else "skip"

    except Exception as e:
        print(f"LLM error: {e}", flush=True)
        return rule_based_agent(clause)


def rule_based_agent(clause: str) -> str:
    risky_keywords = [
        "perpetuity", "irrevocable", "no appeals", "binding arbitration",
        "third parties", "automatic renewal", "liquidated damages",
        "200%", "indemnification", "without notice", "govern",
    ]
    clause_lower = clause.lower()
    if any(kw in clause_lower for kw in risky_keywords):
        return "mark_risky"
    return "mark_safe"


def choose_action(clause: str) -> str:
    try:
        return call_openai(clause)
    except Exception:
        return rule_based_agent(clause)


def run(task: str = "easy", seed: int = 42) -> dict:
    print(f"[START] task={task}", flush=True)

    reset_resp = requests.post(
        f"{BASE_URL}/reset",
        json={"task": task, "seed": seed},
        timeout=10,
    )
    reset_resp.raise_for_status()
    obs = reset_resp.json()

    done = False
    total_reward = 0.0
    steps = 0

    while not done:
        action = choose_action(obs["clause"])

        step_resp = requests.post(
            f"{BASE_URL}/step",
            json={"action": action},
            timeout=10,
        )
        step_resp.raise_for_status()
        result = step_resp.json()

        total_reward += result["reward"]
        steps += 1

        print(f"[STEP] step={steps} reward={result['reward']}", flush=True)

        done = result["done"]
        if not done and result["observation"]:
            obs = result["observation"]

    raw_score = (total_reward / steps) if steps > 0 else 0.5

    # clamp strictly between (0,1)
    final_score = min(max(raw_score, 0.01), 0.99)
    final_score = round(final_score, 4)

    print(f"[END] task={task} score={final_score} steps={steps}", flush=True)

    return {"task": task, "steps": steps, "final_score": final_score}


if __name__ == "__main__":
    tasks = ["easy", "medium", "hard"]

    for task in tasks:
        try:
            run(task=task)
        except Exception as e:
            print(f"[ERROR] task={task} error={e}", flush=True)
