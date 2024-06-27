import os

import pandas as pd
from rec_algorithms.hybrid_rec_system import HybridRecommendationSystem

from rec_algorithms.rec_services.dataset import Dataset
from rec_algorithms.rec_services.user import User


def main():
    participants_path = os.path.join("..", "..", "data", "participants.json")
    answers_path = os.path.join("..", "..", "data", "answers.json")

    with open(participants_path, "r") as f:
        participants = pd.read_json(f)
    with open(answers_path, "r") as f:
        answers = pd.read_json(f)
    data = Dataset(answers, participants)

    user_id = int(input("Enter user id: "))

    user = User(
        user_id,
        data.get_user_vector(user_id),
        data.participants.loc[user_id]["subscription_ids"],
    )
    recommendation_system = HybridRecommendationSystem(user, data)
    recommendation_system.process_user_recommendations()


if __name__ == "__main__":
    main()
