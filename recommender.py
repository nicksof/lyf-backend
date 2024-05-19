import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

df = pd.read_csv('hobbylist.csv')
df['Type'] = df['Type'].fillna('')

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['Type'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

indices = pd.Series(df.index, index=df['Hobby-name']).drop_duplicates()

def get_hobbies(type):
    hobbies = df[df['Type'].str.contains(type, case=False)]
    
    return hobbies['Hobby-name'].tolist()

def get_recommendations(hobbies, cosine_sim=cosine_sim, num_recomm=10, final_recomm=2):
    hobby = random.choice(hobbies)

    idx = indices[hobby]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_sim = sim_scores[1: num_recomm+1]
    final_sim = random.sample(top_sim, min(final_recomm, len(top_sim)))
    hobby_indices = [i[0] for i in final_sim]
    
    recommendations = []
    recommendations.extend(df['Hobby-name'].iloc[hobby_indices].tolist())

    return recommendations


