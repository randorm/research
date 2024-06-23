from typing import List

import faiss
import numpy as np


class User:

    def __init__(self, user_id: int, user_vector: np.ndarray):
        self.id = user_id
        self.black_list = []
        self.user_vector = user_vector
        self.checked = []

    def get_similar_users(
        self, index: faiss.IndexFlatL2, contiguous_to_custom: dict, n: int
    ) -> List[int]:

        distances, indices = index.search(self.user_vector, n)

        try:
            return [
                contiguous_to_custom[i]
                for i in indices[0]
                if self.id != contiguous_to_custom[i]
            ]
        except KeyError:
            return []

    def is_blacklisted(self, some_user_id) -> bool:
        return some_user_id in self.black_list
