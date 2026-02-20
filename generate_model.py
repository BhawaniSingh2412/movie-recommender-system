"""
Script to generate the pickle model files (movie_list.pkl and similarity.pkl)
from the TMDB 5000 Movies dataset.

This replicates the logic from the Kaggle notebook.
"""
import os
import ast
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Download dataset if not present ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MOVIES_CSV = os.path.join(DATA_DIR, 'tmdb_5000_movies.csv')
CREDITS_CSV = os.path.join(DATA_DIR, 'tmdb_5000_credits.csv')

if not os.path.exists(MOVIES_CSV) or not os.path.exists(CREDITS_CSV):
    print("CSV files not found in data/ directory.")
    print("Please download the TMDB 5000 Movie Dataset from Kaggle:")
    print("  https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata")
    print(f"Place tmdb_5000_movies.csv and tmdb_5000_credits.csv in: {DATA_DIR}")
    exit(1)

print("Loading CSV files...")
movies = pd.read_csv(MOVIES_CSV)
credits = pd.read_csv(CREDITS_CSV)

print("Merging datasets...")
movies = movies.merge(credits, on='title')
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

def convert3(text):
    L = []
    counter = 0
    for i in ast.literal_eval(text):
        if counter < 3:
            L.append(i['name'])
        counter += 1
    return L

def fetch_director(text):
    L = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

def collapse(L):
    L1 = []
    for i in L:
        L1.append(i.replace(" ", ""))
    return L1

print("Processing features...")
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: x[0:3])
movies['crew'] = movies['crew'].apply(fetch_director)

movies['cast'] = movies['cast'].apply(collapse)
movies['crew'] = movies['crew'].apply(collapse)
movies['genres'] = movies['genres'].apply(collapse)
movies['keywords'] = movies['keywords'].apply(collapse)

movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

new = movies.drop(columns=['overview', 'genres', 'keywords', 'cast', 'crew'])
new['tags'] = new['tags'].apply(lambda x: " ".join(x))

print("Building similarity matrix...")
cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(new['tags']).toarray()
similarity = cosine_similarity(vector)

# Save pickle files
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
os.makedirs(MODEL_DIR, exist_ok=True)

movie_list_path = os.path.join(MODEL_DIR, 'movie_list.pkl')
similarity_path = os.path.join(MODEL_DIR, 'similarity.pkl')

print(f"Saving model files to {MODEL_DIR}...")
pickle.dump(new, open(movie_list_path, 'wb'))
pickle.dump(similarity, open(similarity_path, 'wb'))

print(f"Done! Generated:")
print(f"  {movie_list_path}")
print(f"  {similarity_path}")
print(f"  Movies count: {len(new)}")
