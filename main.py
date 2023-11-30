# main.py
import streamlit as st

st.title('Movie Recommendation')
st.text('국민대학교 인공지능응용 5조')

movie_input = st.text_input(label='Please enter the movie title')

MOVIE_LIST = ['A', 'B', 'C', 'D', 'E']
my_choice = st.selectbox('Please select a movie title', MOVIE_LIST)
