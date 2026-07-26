import streamlit as st
import pandas as pd
import pickle
import joblib
import requests

# ===============================
# CONFIG
# ===============================

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Replace with your TMDB API key
API_KEY = "abfbb58f334569fa986c10ffdbd85813"

# ===============================
# CUSTOM CSS
# ===============================

st.markdown("""
<style>

.stApp{
    background: linear-gradient(135deg,#141E30,#243B55);
}

h1,h2,h3,h4{
    color:white;
}

p,label{
    color:white;
}

div[data-baseweb="select"]{
    background:white;
    border-radius:12px;
}

div.stButton > button{
    width:100%;
    background:#E50914;
    color:white;
    border:none;
    border-radius:10px;
    padding:12px;
    font-size:18px;
    font-weight:bold;
}

div.stButton > button:hover{
    background:#ff2b2b;
}

.movie-card{
    background:#1f2937;
    border-radius:15px;
    padding:10px;
    text-align:center;
    box-shadow:0px 4px 15px rgba(0,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

# ===============================
# LOAD DATA
# ===============================

with open("movies.pkl", "rb") as f:
    movies = pickle.load(f)

similarity = joblib.load("similarity.joblib")

# ===============================
# FUNCTIONS
# ===============================

def recommend(movie):

    index = movies[movies["title"] == movie].index[0]

    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended = []

    for i in movie_list:
        recommended.append(movies.iloc[i[0]].title)

    return recommended

def recommend_by_cast(actor):

    actor = actor.replace(" ", "").lower()

    movie_list = movies[
        movies["cast"].str.contains(actor, na=False)
    ]

    return movie_list["title"].tolist()

def recommend_by_director(director):

    director = director.replace(" ","").lower()

    movie_list = movies[
        movies["crew"].str.contains(director, na=False)
    ]

    return movie_list["title"].tolist()

def fetch_movie(movie):

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie}"

    response = requests.get(url).json()

    if len(response["results"]) == 0:
        return None

    result = response["results"][0]

    poster = None

    if result["poster_path"]:
        poster = "https://image.tmdb.org/t/p/w500" + result["poster_path"]

    return {"poster": poster}

# ===============================
# HEADER
# ===============================

st.markdown(
"""
<h1 style='text-align:center;color:#E50914;'>
🎬 AI Movie Recommendation System
</h1>

<p style='text-align:center;font-size:20px;'>
Find movies similar to your favourites
</p>
""",
unsafe_allow_html=True
)

st.divider()

# ===============================
# SELECT MOVIE
# ===============================

option = st.radio(
    "Recommendation Type",
    [
        "Movie",
        "Actor",
        "Director"
    ],
    horizontal=True
)

if option == "Movie":

    selected = st.selectbox(
    label="Movie Search",
    options=sorted(movies["title"].unique()),
    placeholder="Search for a movie...",
    label_visibility="collapsed"
)

elif option == "Actor":

    actors = sorted({
        actor
        for cast in movies["cast"]
        for actor in cast.split()
    })

    selected = st.selectbox(
    label="Actor Search",
    options=actors,
    placeholder="Search for an actor...",
    label_visibility="collapsed"
)
else:

    directors = sorted({director for crew in movies["crew"] for director in crew.split() })
    selected = st.selectbox(
    label="Director Search",
    options=directors,
    placeholder="Search for a director...",
    label_visibility="collapsed"
)
    
# ===============================
# SHOW SELECTED MOVIE
# ===============================

if option == "Movie":

    info = fetch_movie(selected)

    if info:

        left, right = st.columns([1,2])

        with left:
            if info["poster"]:
                st.image(info["poster"])

        with right:
            st.subheader(selected.upper())

    st.divider()

# ===============================
# RECOMMEND BUTTON
# ===============================

if st.button("🎥 Recommend Movies"):

    with st.spinner("Finding similar movies..."):

        if option == "Movie":
            recommendations = recommend(selected)

        elif option == "Actor":
            recommendations = recommend_by_cast(selected)

        else:
            recommendations = recommend_by_director(selected)

    if option == "Movie":
        st.subheader("Similar Movies")

    elif option == "Actor":
        st.subheader(f"Movies featuring {selected.title()}")

    else:
        st.subheader(f"Movies directed by {selected.title()}")

    cols = st.columns(5)

    for col, movie in zip(cols, recommendations):

        with col:

            data = fetch_movie(movie)

            if data and data["poster"]:
                st.image(data["poster"])

            st.markdown(f"### {movie.upper()}")

