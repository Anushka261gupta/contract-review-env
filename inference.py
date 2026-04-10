# inference.py
"""
Inference script: runs an AI agent against the contract review environment.
Fully compliant with OpenEnv Hackathon requirements.
"""

import os
import json
import requests
from openai import OpenAI

# Required environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Environment endpoint
BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

# OpenAI client (proxy)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

VALID_ACTIONS = ["mark_safe", "mark_risky", "skip", "suggest_edit"]


def call_openai(clause: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
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

        # Smart behavior
        if action == "mark_risky" and suggestion:
            action = "suggest_edit"

        return action if action in VALID_ACTIONS else "skip"

    except Exception as e:
        print(f"LLM error: {e}", flush=True)
        return "skip"


def run(task: str = "easy", seed: int = 42):
    print(f"[START] task={task} env=contract-review model={MODEL_NAME}", flush=True)

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
    rewards_list = []  

    while not done:
        action = call_openai(obs["clause"])

        step_resp = requests.post(
            f"{BASE_URL}/step",
            json={"action": action},
            timeout=10,
        )
        step_resp.raise_for_status()
        result = step_resp.json()

        reward = result["reward"]
        total_reward += reward
        rewards_list.append(reward)
        steps += 1

        done = result["done"]

        print(
            f"[STEP] step={steps} action={action} reward={reward:.2f} done={str(done).lower()} error=null",
            flush=True
        )

        if not done and result["observation"]:
            obs = result["observation"]

    raw_score = (total_reward / steps) if steps > 0 else 0.5
    final_score = min(max(raw_score, 0.01), 0.99)

    success = "true" if final_score > 0.5 else "false"
    rewards_str = ",".join([f"{r:.2f}" for r in rewards_list])

    print(f"[END] success={success} steps={steps} rewards={rewards_str}", flush=True)


if __name__ == "__main__":
    tasks = ["easy", "medium", "hard"]

    for task in tasks:
        try:
            run(task=task)
        except Exception as e:
            print(f"[END] success=false steps=0 rewards= error={e}", flush=True)
