import numpy as np
import pandas as pd


class Dataset:
    """
    Dataset class that represents the participants and their answers.

    Args:
        :param answers_data: DataFrame with answers data
        :param participants_data: DataFrame with participants data

    """

    def __init__(self, answers_data: pd.DataFrame, participants_data: pd.DataFrame):
        self.participants = participants_data.copy()
        self.answers = answers_data.copy()
        self.answers_pivot = answers_data.pivot(
            index="respondent_id", columns="field_id", values="option"
        )
        self.nan_responses = None

        self.remove_nan_responses()

    def contiguous_to_custom_index(self) -> dict:
        """Returns a dictionary that maps the contiguous index to the custom index.
            FAISS library uses contiguous index, so we need to map it to the custom index, because some participants can be removed.

        Returns:
            dict: Dictionary that maps the contiguous index to the custom index
        """
        return {i: j for i, j in enumerate(self.answers_pivot.index)}

    def custom_to_contiguous_index(self) -> dict:
        """Returns a dictionary that maps the custom index to the contiguous index.

        Returns:
            dict: Dictionary that maps the custom index to the contiguous index
        """
        return {j: i for i, j in enumerate(self.answers_pivot.index)}

    def get_user_vector(self, user_id: int) -> np.ndarray:
        """Returns the user vector containing the numerical answers of the user_id.

        Args:
            :param user_id: User id

        Returns:
            np.ndarray: User vector
        """
        return self.answers_pivot.loc[user_id].values.reshape(1, -1).astype(np.float32)

    def remove_nan_responses(self) -> None:
        """Removes all participants with NaN responses. If a participant has at least one NaN response, it is removed."""
        nan_responses = self.answers_pivot.isna().sum(axis=1)
        self.nan_responses = nan_responses[nan_responses > 0].index.to_list()

        for i in self.nan_responses:
            self.answers_pivot = self.answers_pivot.drop(i)
            self.participants = self.participants.drop(i)


__all__ = ("Dataset",)
