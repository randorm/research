import enum
import os

import faiss
import numpy as np
import pandas as pd
from rec_services.dataset import Dataset

from rec_services.graph import Graph
from rec_services.user import User
from sklearn.preprocessing import normalize


class StatusKind(enum.Enum):
    COMMON = 1
    FRIEND = 2


class RecommendationSystem:
    status = StatusKind.COMMON

    def __init__(self, user: User, dataset: Dataset):
        self.user = user

        self.participants = dataset.participants
        self.answers_pivot = dataset.answers_pivot
        self.working_answers = dataset.answers_pivot.drop(self.user.black_list)

        self.working_graph = Graph(self.participants)

        self.index = faiss.IndexFlatL2(self.answers_pivot.shape[1])
        self.index.add(
            np.ascontiguousarray(
                normalize(self.working_answers.values).astype(np.float32)
            )
        )

        self.contiguous_to_custom = dataset.contiguous_to_custom_index()
        self.custom_to_contiguous = dataset.custom_to_contiguous_index()

    def create_faiss_index(self) -> None:
        self.index = faiss.IndexFlatL2(self.working_answers.shape[1])
        normalized_data = normalize(self.working_answers.values).astype(np.float32)
        self.index.add(np.ascontiguousarray(normalized_data))

    def update_faiss_index(self) -> None:

        self.working_answers = self.answers_pivot.drop(self.user.black_list)
        self.contiguous_to_custom = {
            i: j for i, j in enumerate(self.working_answers.index)
        }
        self.custom_to_contiguous = {
            j: i for i, j in enumerate(self.working_answers.index)
        }

        self.create_faiss_index()

    def process_user_recommendations(self) -> None:

        similar_users = self.user.get_similar_users(
            self.index, self.contiguous_to_custom, 11
        )
        neighbor_users = self.working_graph.get_n_neighbors(self.user.id, 11)

        while self.working_answers.shape[0] - 2 != len(neighbor_users):

            if len(similar_users) == 0 and self.status == StatusKind.COMMON:
                neighbor_users = self.working_graph.get_n_neighbors(self.user.id, 11)

                if len(neighbor_users) == 0:
                    similar_users = self.user.get_similar_users(
                        self.index, self.contiguous_to_custom, 11
                    )

                    if len(similar_users) == 0:
                        break
                    self.status = StatusKind.COMMON
                else:
                    neighbor_user = User(
                        neighbor_users[0],
                        self.answers_pivot.loc[neighbor_users[0]]
                        .values.reshape(1, -1)
                        .astype(np.float32),
                    )

                    similar_users = neighbor_user.get_similar_users(
                        self.index, self.contiguous_to_custom, 11
                    )
                    # self.working_graph.remove_edge(self.user.id, neighbor_users[0])

                    del neighbor_users[0]

                    if self.user.id in similar_users:
                        idx = similar_users.index(self.user.id)

                        del similar_users[idx]
                    self.status = StatusKind.FRIEND
            elif len(similar_users) == 0 and self.status == StatusKind.FRIEND:
                similar_users = self.user.get_similar_users(
                    self.index, self.contiguous_to_custom, 11
                )
                self.status = StatusKind.COMMON
            if self.user.is_blacklisted(similar_users[0]):
                self.update_faiss_index()
                similar_users = self.user.get_similar_users(
                    self.index, self.contiguous_to_custom, 11
                )
                continue
            if similar_users[0] in self.working_graph.get_neighbors(self.user.id):
                if len(similar_users) == 10 and all(
                    i in self.working_graph.get_neighbors(self.user.id)
                    for i in similar_users
                ):

                    for i in similar_users:
                        self.user.black_list.append(i)
                    self.update_faiss_index()

                    continue
                del similar_users[0]

                continue
            self.answer_handler(similar_users)

            del similar_users[0]
        self.restart_handler()

    def answer_handler(self, similar_users) -> None:
        while True:
            print(f"Do you want this user {similar_users[0]} to be your friend?")
            print(
                np.array(
                    self.answers_pivot[self.answers_pivot.index == similar_users[0]]
                )
            )
            ans = input("yes/no: ")

            match ans:

                case "yes":
                    print(f"You have a new friend {similar_users[0]}")
                    print("----------------------------------------")
                    self.working_graph.add_edge(self.user.id, similar_users[0])
                    break
                case "no":
                    print(f"You have no new friend")
                    print("----------------------------------------")
                    self.user.black_list.append(similar_users[0])
                    self.update_faiss_index()
                    break
                case _:
                    print("Invalid input. Use only yes or no.")

    def restart_handler(self) -> None:
        print("No more users to recommend. I restart the recommendation process.")

        self.user.black_list = []

        self.working_graph = Graph(self.participants)
        self.create_faiss_index()
        self.process_user_recommendations()


def main():
    participants_path = os.path.join("..", "..", "data", "participants.json")
    answers_path = os.path.join("..", "..", "data", "answers.json")

    with open(participants_path, "r") as f:
        participants = pd.read_json(f)
    with open(answers_path, "r") as f:
        answers = pd.read_json(f)
    data = Dataset(answers, participants)

    user_id = int(input("Enter user id: "))

    user = User(user_id, data.get_user_vector(user_id))
    recommendation_system = RecommendationSystem(user, data)
    recommendation_system.process_user_recommendations()


if __name__ == "__main__":
    main()
