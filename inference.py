from env import ContractEnv
from grader import evaluate_episode
import random

def run():
    env = ContractEnv()
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
    print("Score:", score)

if __name__ == "__main__":
    run()