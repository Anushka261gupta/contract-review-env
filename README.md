---
title: Contract Review Env
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# Contract Review AI Environment

This project implements an OpenEnv-compatible environment for training AI agents to analyze contract clauses.

## Features
- Clause-level risk detection (safe vs risky)
- Multi-level tasks (easy, medium, hard)
- Reward-based environment for agent learning
- Grader system with 0–1 scoring
- FastAPI endpoints for evaluation

## Endpoints
- /tasks → returns task definitions
- /baseline → runs baseline agent
- /grader → evaluates agent performance

## Deployment
Deployed using Docker and FastAPI.

final fix
