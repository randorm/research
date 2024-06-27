import enum

import faiss
import numpy as np
from rec_services.dataset import Dataset

from rec_services.graph import Graph
from rec_services.user import User
from sklearn.preprocessing import normalize


class StatusKind(enum.Enum):
    """StatusKind enum class that holds the status of the users' flow now."""

    COMMON = 1
    FRIEND = 2


class HybridRecommendationSystem:
    """Recommendation system class that handles the recommendation process.

    Args:
        :param user: User object
        :param dataset: Dataset object

    """

    status = StatusKind.COMMON

    def __init__(self, user: User, dataset: Dataset):
        self.user = user

        self.participants = dataset.participants
        self.answers_pivot = dataset.answers_pivot
        self.working_answers = dataset.answers_pivot.drop(self.user.black_list)

        self.working_graph = Graph(self.participants, dataset.nan_responses)

        self.index = faiss.IndexFlatL2(self.working_answers.shape[1])
        self.index.add(
            np.ascontiguousarray(
                normalize(self.working_answers.values).astype(np.float32)
            )
        )

        self.contiguous_to_custom = dataset.contiguous_to_custom_index()
        self.custom_to_contiguous = dataset.custom_to_contiguous_index()

    def create_faiss_index(self) -> None:
        """Creates a new faiss index and adds the normalized data to it."""
        self.index = faiss.IndexFlatL2(self.working_answers.shape[1])
        normalized_data = normalize(self.working_answers.values).astype(np.float32)
        self.index.add(np.ascontiguousarray(normalized_data))

    def update_faiss_index(self) -> None:
        """Updates the faiss index by removing blacklisted users."""
        self.working_answers = self.answers_pivot.drop(self.user.black_list)
        self.contiguous_to_custom = {
            i: j for i, j in enumerate(self.working_answers.index)
        }
        self.custom_to_contiguous = {
            j: i for i, j in enumerate(self.working_answers.index)
        }

        self.create_faiss_index()

    def process_user_recommendations(self) -> None:
        """Processes the user recommendations.

        The function gets similar users and asks the user if they want to be friends.
           If the user says yes, the function adds the user to the graph and the checked list.
           If the user says no, the function adds the user to the blacklist and updates the faiss index.
        When algorithm shows 10 users for recommendations, it recommends the similar users from the first neighbor.

        After the recommendation process is finished, the function restarts the recommendation process.
        As a result, the recommendation process is infinite.
        """

        similar_users = self.user.get_similar_users(
            self.index, self.contiguous_to_custom, 11
        )

        while self.working_answers.shape[0] != len(self.user.checked) - 1:
            neighbor_users = self.working_graph.get_n_neighbors(self.user.id, 11)

            if (
                len(similar_users) == 0 and self.status == StatusKind.COMMON
            ):  # check if similar users are empty for the common user

                if len(neighbor_users) == 0:  # check if neighbors' list is empty, too
                    similar_users = self.user.get_similar_users(
                        self.index, self.contiguous_to_custom, 11
                    )

                    if len(similar_users) == 0:
                        break
                else:
                    neighbor_user = User(
                        neighbor_users[0],
                        self.working_answers.loc[neighbor_users[0]]
                        .values.reshape(1, -1)
                        .astype(np.float32),
                        self.participants.loc[neighbor_users[0]]["subscription_ids"],
                    )

                    similar_users = neighbor_user.get_similar_users(
                        self.index, self.contiguous_to_custom, 11
                    )  # get similar users for the neighbor user

                    self.user.checked.append(neighbor_users[0])

                    if (
                        self.user.id in similar_users
                    ):  # we don't want to recommend the user itself, if it is in the similar users list of the neighbor user
                        idx = similar_users.index(self.user.id)

                        del similar_users[idx]
                    self.status = StatusKind.FRIEND
            elif (
                len(similar_users) == 0 and self.status == StatusKind.FRIEND
            ):  # check if similar users are empty for the neighbor user
                similar_users = self.user.get_similar_users(
                    self.index, self.contiguous_to_custom, 11
                )
                self.status = StatusKind.COMMON
            if self.user.is_blacklisted(
                similar_users[0]
            ):  # we don't want to recommend the rejected users
                continue
            if self.user.is_checked(
                similar_users[0]
            ):  # we don't want to recommend the already checked users
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
        """Handles the user's answer to the recommendation.

        Args:
            :param similar_users: List of similar users

        """
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
                    self.user.checked.append(similar_users[0])

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
        """Handles the restart of the recommendation process."""
        print("No more users to recommend. I restart the recommendation process.")

        self.user.black_list = []

        self.working_answers = self.answers_pivot
        self.update_faiss_index()

        self.process_user_recommendations()
