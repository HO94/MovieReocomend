# D:\국민대\인공지능응용3\movie_backup
# main.py
import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import requests

st.title('Movie Recommendation')
st.text('국민대학교 인공지능응용 5조')


headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzZDE3M2UyMzlmNzEwNmNlNTA4M2I1MGI4ZjU1M2U0NiIsInN1YiI6IjY1Njg4YjAzMDljMjRjMDExYmU3MmFlNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.a_uICMVt4DygQzVWT-nQeDwYYQQxvxDM2Ho0_oe7MdQ"
}

url_dict = {
    # 'discover' : f'https://api.themoviedb.org/3/movie/now_playing?language=en-EN&page={pageNum}&region=KR',
    'nowPlaying' : f'https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1&region=KR',
    'popular' : f'https://api.themoviedb.org/3/movie/popular?language=en-US&page=1&region=KR',
    'upComing' : f'https://api.themoviedb.org/3/movie/upcoming?language=en-US&page=1&region=KR'
    }


# 기존 영화 목록
movies = pd.read_csv('./data/tmdb_5000_movies.csv')
MOVIE_LIST = movies['title']
my_choice = st.selectbox('Please select a movie title', MOVIE_LIST)



def cal_cosine_sim(response_df, sample=False):
    if sample == False:
        choice_df = movies[movies['title'] == my_choice][['id', 'title', 'overview']]
        choice_df.rename(columns = {'id' : 'movie_id'}, inplace=True)
        response_df = pd.concat([response_df, choice_df], axis = 0).reset_index(drop=True)
    
    tfidf = TfidfVectorizer(stop_words='english')
    response_df['overview'] = response_df['overview'].fillna('')
    tfidf_matrix = tfidf.fit_transform(response_df['overview'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(response_df.index, index=response_df['title']).drop_duplicates()
    return indices, cosine_sim

def get_recommendations(response_df, title, indices, cosine_sim):
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
    return response_df['title'].iloc[movie_indices]


def _get_response(url, headers):
    response = requests.get(url, headers=headers)
    response_dict = response.text
    response_dict = response_dict.replace('false', 'False')
    response_dict = response_dict.replace('null', 'None')
    return eval(response_dict)


def _get_df(response_dict):
    total_result = pd.DataFrame()
    for idx in response_dict['results']:
        sub_result = pd.DataFrame({'movie_id' : [idx['id']],
                                   'title' : [idx['title']],
                                    'overview' : [idx['overview']]})
        total_result = pd.concat([total_result, sub_result], axis=0)
    return total_result


def get_response_df(url, target, headers):
    response_dict = _get_response(url, headers)
    if 'popular' in url:
        # 1page : 20, total 1000
        end_point = 50
    else:
        end_point = response_dict['total_pages']+1
    total_reulst = pd.DataFrame()
    for pages in range(1, end_point):
        
        url_list = {
        # 'discover' : f'https://api.themoviedb.org/3/movie/now_playing?language=en-EN&page={pageNum}&region=KR',
        'nowPlaying' : f'https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={pages}&region=KR',
        'popular' : f'https://api.themoviedb.org/3/movie/popular?language=en-US&page={pages}&region=KR',
        'upComing' : f'https://api.themoviedb.org/3/movie/upcoming?language=en-US&page={pages}&region=KR'
        }
        response_dict = _get_response(url_list[target], headers)
        result = _get_df(response_dict)
        total_reulst = pd.concat([total_reulst, result], axis=0)

    return total_reulst.reset_index(drop=True)

if st.button('Recommend') :
    # 탭 생성 : 첫번째 탭의 이름은 Tab A 로, Tab B로 표시합니다. 
    tab1, tab2, tab3, tab4= st.tabs(['Popular', 'Now Playing' , 'Upcoming', 'sample5000'])

    with tab1:
        popular_url = url_dict['popular']
        st.text(popular_url)
        response_df = get_response_df(popular_url, 'popular', headers)
        indices, cosine_sim = cal_cosine_sim(response_df, sample=False)
        popular_result = get_recommendations(response_df, my_choice, indices, cosine_sim)
        st.text(popular_result)
    with tab2:
        now_url = url_dict['nowPlaying']
        st.text(now_url)
        response_df = get_response_df(now_url, 'nowPlaying', headers)
        indices, cosine_sim = cal_cosine_sim(response_df, sample=False)
        now_result = get_recommendations(response_df, my_choice, indices, cosine_sim)
        st.text(now_result)
    with tab3:
        come_url = url_dict['upComing']
        st.text(come_url)
        response_df = get_response_df(come_url, 'upComing', headers)
        indices, cosine_sim = cal_cosine_sim(response_df, sample=False)
        come_result = get_recommendations(response_df, my_choice, indices, cosine_sim)
        st.text(come_result)
    with tab4:
        indices, cosine_sim = cal_cosine_sim(movies, sample=True)
        result = get_recommendations(response_df, my_choice, indices, cosine_sim)
        st.text(result)


values = st.slider('Please give me feedback', 0, 10, 5, 1 )
