import os

import pandas as pd


def get_info_df(data_path):
    path_to_participants = os.path.join(data_path, 'participants.json')
    path_to_answers = os.path.join(data_path, 'answers.json')

    df1 = pd.read_json(path_to_participants)
    df2 = pd.read_json(path_to_answers)
    df2 = pd.DataFrame(df2.groupby(['respondent_id'])['option'].apply(list))
    df2['id'] = df2.index
    return pd.merge(df1, df2)


if __name__ == "__main__":
    path_to_data = os.path.join('..', '..', '..', 'data')
    path_to_info_df = os.path.join(path_to_data, 'info_df.pkl')
    df = get_info_df(path_to_data)
    df.to_pickle(path_to_info_df)
