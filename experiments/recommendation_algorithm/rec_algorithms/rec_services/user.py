from typing import List

import faiss
import numpy as np


class User:
    """
    User class that represents the user, his interactions and his user vector (answers).

    Args:
        :param user_id: User id
        :param user_vector: User vector
        :param subscription_ids: List of subscription ids from the participants' data
    """

    def __init__(
        self, user_id: int, user_vector: np.ndarray, subscription_ids: List[int]
    ):
        self.id = user_id
        self.black_list = []
        self.user_vector = user_vector
        self.checked = subscription_ids.append(user_id)

    def get_similar_users(
        self, index: faiss.IndexFlatL2, contiguous_to_custom: dict, n: int
    ) -> List[int]:
        """Returns the n most similar users to the user. If there is no similar user, FAISS returns -1.
        This value is handled using try-except block.

        Args:
            :param index: FAISS index
            :param contiguous_to_custom: Dictionary that maps the contiguous index to the custom index
            :param n: Number of similar users to return

        Returns:
            List[int]: List of similar users

        """

        distances, indices = index.search(self.user_vector, n)
        lst = []
        for i in indices[0]:
            try:
                lst.append(contiguous_to_custom[i])
            except KeyError:
                pass
        return lst

    def is_blacklisted(self, some_user_id) -> bool:
        """Checks if the user is blacklisted."""
        return some_user_id in self.black_list

    def is_checked(self, some_user_id) -> bool:
        """Checks if the user is checked."""
        return some_user_id in self.checked


__all__ = ("User",)
