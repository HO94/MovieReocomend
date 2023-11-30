# main.py
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


st.title('Movie Recommendation')
st.text('국민대학교 인공지능응용 5조')

cred = pd.read_csv('./data/tmdb_5000_credits.csv')
movies = pd.read_csv('./data/tmdb_5000_movies.csv')
cred.columns = ['id','tittle','cast','crew']
df= movies.merge(cred,on='id')
m = df['vote_count'].quantile(0.9)
C = df['vote_average'].mean()

MOVIE_LIST = movies['title']
my_choice = st.selectbox('Please select a movie title', MOVIE_LIST)


def _weighted_rating(x, m=m, C=C):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * C)

def cal_cosine_sim(df):
    C = df['vote_average'].mean()
    m = df['vote_count'].quantile(0.9)
    q_movies = df.copy().loc[df['vote_count'] >= m]
    q_movies['score'] = q_movies.apply(_weighted_rating, axis=1)
    q_movies = q_movies.sort_values('score', ascending=False)
    tfidf = TfidfVectorizer(stop_words='english')
    df['overview'] = df['overview'].fillna('')
    tfidf_matrix = tfidf.fit_transform(df['overview'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    return indices, cosine_sim

def get_recommendations(title, indices, cosine_sim):
    # Get the index of the movie that matches the title
    idx = indices[title]
    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:11]
    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]
    # Return the top 10 most similar movies
    return df['title'].iloc[movie_indices]

if st.button('Recommend') :
    indices, cosine_sim = cal_cosine_sim(df)
    result = get_recommendations(my_choice, indices, cosine_sim)
    st.text(result)