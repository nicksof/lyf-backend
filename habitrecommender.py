import pandas as pd

df = pd.read_csv('habitlist.csv')

def get_habits(answer):
    filtered_habit = df[df['Answer'].str.contains(answer)]
    habit = filtered_habit['Habit'].tolist()

    return habit[0]