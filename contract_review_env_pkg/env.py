import random

class ContractEnv:
    def __init__(self):
        self.contracts = {
            "easy": [
                [
                    {"text": "Payment must be made within 30 days.", "label": "safe"},
                    {"text": "Company can terminate anytime without notice.", "label": "risky"}
                ]
            ],

            "medium": [
                [
                    {"text": "Late payment will incur a 5% penalty.", "label": "risky"},
                    {"text": "Both parties must agree before termination.", "label": "safe"}
                ],
                [
                    {"text": "User data may be shared with third parties under policy terms.", "label": "risky"},
                    {"text": "Confidential information must not be disclosed without consent.", "label": "safe"}
                ]
            ],

            "hard": [
                [
                    {"text": "The agreement may be terminated at any time, subject to binding arbitration and indemnification obligations that survive indefinitely.", "label": "risky"},
                    {"text": "Confidential information must not be disclosed, except where required by law or with prior written consent.", "label": "safe"}
                ],
                [
                    {"text": "The client grants the vendor a non-exclusive, perpetual license to use all submitted data for any purpose.", "label": "risky"},
                    {"text": "Liability is limited except in cases of gross negligence, fraud, or breach of confidentiality.", "label": "safe"}
                ]
            ]
}

        self.actions = ["mark_safe", "mark_risky", "skip"]

        self.current_contract = None
        self.current_index = 0

    def reset(self, level="easy"):
        self.current_contract = random.choice(self.contracts[level])
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
            reward = 0.9
        elif action == "mark_safe" and correct == "safe":
            reward = 0.9
        elif action == "skip":
            reward = 0.3
        else:
            reward = 0.1

        self.current_index += 1
        done = self.current_index >= len(self.current_contract)

        # return next state or None if done
        next_obs = self._get_obs() if not done else None

        return next_obs, reward, done, {}