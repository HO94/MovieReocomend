# D:\국민대\인공지능응용3\movie_backup
# main.py
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import requests

st.title('Movie Recommendation')
st.text('국민대학교 인공지능응용 5조')

pageNum= 1
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzZDE3M2UyMzlmNzEwNmNlNTA4M2I1MGI4ZjU1M2U0NiIsInN1YiI6IjY1Njg4YjAzMDljMjRjMDExYmU3MmFlNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.a_uICMVt4DygQzVWT-nQeDwYYQQxvxDM2Ho0_oe7MdQ"
}

url_dict = {
    # 'discover' : f'https://api.themoviedb.org/3/movie/now_playing?language=en-EN&page={pageNum}&region=KR',
    'nowPlaying' : f'https://api.themoviedb.org/3/movie/now_playing?language=ko-KR&page={pageNum}&region=KR',
    'popular' : f'https://api.themoviedb.org/3/movie/popular?language=ko-KR&page={pageNum}&region=KR',
    'upComing' : f'https://api.themoviedb.org/3/movie/upcoming?language=ko-KR&page={pageNum}&region=KR'
    }


# 기존 영화 목록
movies = pd.read_csv('./data/tmdb_5000_movies.csv')
MOVIE_LIST = movies['title']
my_choice = st.selectbox('Please select a movie title', MOVIE_LIST)



def cal_cosine_sim(df):
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
    return movies['title'].iloc[movie_indices]

def _get_response_df(response):
    total_result = pd.DataFrame()
    for idx in response['results']:
        sub_result = pd.DataFrame({'movie_id' : [idx['id']],
                    'overview' : [idx['overview']]})
        total_result = pd.concat([total_result, sub_result], axis=0)
    return response_df

def get_response(url, headers):
    response = requests.get(url, headers=headers)
    response_df = _get_response_df(response.text)
    if 'popular' in url:
        # 1page : 20, total 1000
        end_point = 50
    else:
        end_point = response['total_pages']+1
    for pages in range(2, end_point):
        pageNum = pages
        response = requests.get(url_dict['popular'], headers=headers)
        response_df = pd.concat([response_df, _get_response_df(response)], axis=0)
    return response_df

if st.button('Recommend') :
    # 탭 생성 : 첫번째 탭의 이름은 Tab A 로, Tab B로 표시합니다. 
    tab1, tab2, tab3, tab4= st.tabs(['Popular', 'Now Playing' , 'Upcoming', 'sample5000'])

    with tab1:
        url = url_dict['popular']
        response_df = get_response(url, headers)
        indices, cosine_sim = cal_cosine_sim(response_df)
        result = get_recommendations(my_choice, indices, cosine_sim)
        st.text(result)
    with tab2:
        url = url_dict['nowPlaying']
        response_df = get_response(url, headers)
        indices, cosine_sim = cal_cosine_sim(response_df)
        result = get_recommendations(my_choice, indices, cosine_sim)
        st.text(result)
    with tab3:
        url = url_dict['upComing']
        response_df = get_response(url, headers)
        indices, cosine_sim = cal_cosine_sim(response_df)
        result = get_recommendations(my_choice, indices, cosine_sim)
        st.text(result)
    with tab4:
        indices, cosine_sim = cal_cosine_sim(movies)
        result = get_recommendations(my_choice, indices, cosine_sim)
        st.text(result)


values = st.slider('Please give me feedback', 0, 10, 5, 1 )
