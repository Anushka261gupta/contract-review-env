import random

class ContractEnv:
    def __init__(self):
        self.contracts = [
            [
                {"text": "Payment must be made within 30 days.", "label": "safe"},
                {"text": "Company can terminate anytime without notice.", "label": "risky"}
            ],
            [
                {"text": "Late payment will incur a 5% penalty.", "label": "risky"},
                {"text": "Both parties must agree before termination.", "label": "safe"}
            ],
            [
                {"text": "User data may be shared with third parties.", "label": "risky"},
                {"text": "Confidential information must not be disclosed.", "label": "safe"}
            ],
            [
                {"text": "Intellectual property will be protected.", "label": "safe"},
                {"text": "Software updates are mandatory.", "label": "risky"}
            ],
            [
                {"text": "Liability is limited to the contract value.", "label": "safe"},
                {"text": "Force majeure events are not covered.", "label": "risky"}
            ]
        ]

        self.actions = ["mark_safe", "mark_risky", "skip"]

        self.current_contract = None
        self.current_index = 0

    def reset(self):
        self.current_contract = random.choice(self.contracts)
        self.current_index = 0
        return self._get_obs()

    def _get_obs(self):
        return {
            "clause": self.current_contract[self.current_index]["text"],
            "clause_number": self.current_index
        }

    def step(self, action):
        clause = self.current_contract[self.current_index]
        correct = clause["label"]

        if action == "mark_risky" and correct == "risky":
            reward = 1
        elif action == "mark_safe" and correct == "safe":
            reward = 1
        elif action == "skip":
            reward = 0.2
        else:
            reward = -1

        self.current_index += 1
        done = self.current_index >= len(self.current_contract)

        # return next state or None if done
        next_obs = self._get_obs() if not done else None

        return next_obs, reward, done, {}
