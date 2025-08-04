import pandas as pd

df = pd.read_csv('/Users/dakshin/Developer Projects/ai/DataScience-Projects/blockchain_trade/data/trading_persona_dataset.csv')

user_lst = list(df.user_id.unique())

for num, user in enumerate(user_lst):
    df[df['user_id'] == user].to_csv(f'data/user-{user[1:]}.csv')