def evaluate_episode(actions, ground_truth):
    """
    actions: list of actions taken by agent
    ground_truth: list of correct labels (safe/risky)
    """

    correct = 0
    total = len(ground_truth)

    for act, truth in zip(actions, ground_truth):
        if act == "mark_safe" and truth == "safe":
            correct += 1
        elif act == "mark_risky" and truth == "risky":
            correct += 1

    score = correct / total if total > 0 else 0

    return score