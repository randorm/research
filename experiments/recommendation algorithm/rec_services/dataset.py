import numpy as np
import pandas as pd


class Dataset:

    def __init__(self, answers_data: pd.DataFrame, participants_data: pd.DataFrame):
        self.participants = participants_data.copy()
        self.answers = answers_data.copy()
        self.answers_pivot = answers_data.pivot(
            index="respondent_id", columns="field_id", values="option"
        )

        self.remove_nan_responses()

    def contiguous_to_custom_index(self):
        return {i: j for i, j in enumerate(self.answers_pivot.index)}

    def custom_to_contiguous_index(self):
        return {j: i for i, j in enumerate(self.answers_pivot.index)}

    def get_user_vector(self, user_id: int):
        return self.answers_pivot.loc[user_id].values.reshape(1, -1).astype(np.float32)

    def remove_nan_responses(self) -> None:
        nan_responses = self.answers_pivot.isna().sum(axis=1)
        nan_indices = nan_responses[nan_responses > 0].index

        self.answers_pivot = self.answers_pivot.drop(nan_indices)
        self.participants = self.participants.drop(nan_indices)
