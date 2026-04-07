TASKS = [
    {
        "name": "easy_risk_detection",
        "description": "Identify whether a clause is safe or risky",
        "actions": ["mark_safe", "mark_risky", "skip"]
    },
    {
        "name": "medium_clause_classification",
        "description": "Classify clauses with moderate ambiguity into categories such as payment, termination, and privacy",
        "actions": ["payment", "termination", "privacy", "legal"]
    },
    {
        "name": "hard_contract_review",
        "description": "Analyze complex clauses with mixed legal signals, detect risk, and provide reasoning in realistic contract scenarios",
        "actions": ["mark_safe", "mark_risky", "suggest_edit"]
    }
]