TASKS = [
    {
        "name": "easy_risk_detection",
        "description": "Identify whether a clause is safe or risky",
        "actions": ["mark_safe", "mark_risky", "skip"]
    },
    {
        "name": "medium_clause_classification",
        "description": "Classify clause into categories like payment, termination, privacy",
        "actions": ["payment", "termination", "privacy", "legal"]
    },
    {
        "name": "hard_contract_review",
        "description": "Analyze clause, detect risk, and provide reasoning",
        "actions": ["mark_safe", "mark_risky", "suggest_edit"]
    }
]
