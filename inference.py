# inference.py
"""
Inference script: runs an AI agent against the contract review environment.
Uses OpenAI API if OPENAI_API_KEY is set; falls back to rule-based agent.
"""

import os
import json
import requests
from typing import Optional
from openai import OpenAI

BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
                        "Given a contract clause, respond with exactly one of: "
                        "mark_safe, mark_risky, skip, suggest_edit."
                    ),
                },
                {"role": "user", "content": clause},
            ],
        )

        action = response.choices[0].message.content.strip().lower()
        return action if action in VALID_ACTIONS else "skip"

    except Exception as e:
        print(f"LLM error: {e}", flush=True)
        return rule_based_agent(clause)


def rule_based_agent(clause: str) -> str:
    """Deterministic fallback agent based on keyword matching."""
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
    if OPENAI_API_KEY:
        return call_openai(clause)
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
    history = []

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

        history.append({
            "clause": obs["clause"],
            "action": action,
            "reward": result["reward"],
            "correct_label": result["info"].get("correct_label"),
        })

        done = result["done"]
        if not done and result["observation"]:
            obs = result["observation"]

    final_score = round(total_reward / steps, 4) if steps > 0 else 0.0

    print(f"[END] task={task} score={final_score} steps={steps}", flush=True)

    return {"task": task, "steps": steps, "final_score": final_score}


if __name__ == "__main__":
    import sys
    task = sys.argv[1] if len(sys.argv) > 1 else "easy"
    run(task=task)
