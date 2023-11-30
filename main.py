# main.py
import streamlit as st
import pandas as pd

st.title('Movie Recommendation')
st.text('국민대학교 인공지능응용 5조')

cred = pd.read_csv('./data/tmdb_5000_credits.csv')
movies = pd.read_csv('./data/tmdb_5000_movies.csv')

MOVIE_LIST = movies['title']
my_choice = st.selectbox('Please select a movie title', MOVIE_LIST)

