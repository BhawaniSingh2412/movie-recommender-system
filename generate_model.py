"""
Generate pickle model files (movie_list.pkl and similarity.pkl)
from The Movies Dataset (45,000+ movies from Kaggle).

We filter to movies with at least 1 vote to keep the dataset practical
while still being much larger than the original TMDB 5000 dataset.

Dataset: https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
"""
import os
import ast
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')

# --- Load datasets ---
MOVIES_CSV = os.path.join(DATA_DIR, 'movies_metadata.csv')
CREDITS_CSV = os.path.join(DATA_DIR, 'credits.csv')
KEYWORDS_CSV = os.path.join(DATA_DIR, 'keywords.csv')

for f in [MOVIES_CSV, CREDITS_CSV, KEYWORDS_CSV]:
    if not os.path.exists(f):
        print(f"Missing: {f}")
        print("Download 'The Movies Dataset' from Kaggle:")
        print("  https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset")
        exit(1)

print("Loading CSV files...")
meta = pd.read_csv(MOVIES_CSV, low_memory=False)
credits = pd.read_csv(CREDITS_CSV)
keywords = pd.read_csv(KEYWORDS_CSV)

# --- Clean movie IDs (some rows have bad/non-numeric IDs) ---
meta = meta[meta['id'].apply(lambda x: str(x).isdigit())]
meta['id'] = meta['id'].astype(int)
credits['id'] = credits['id'].astype(int)
keywords['id'] = keywords['id'].astype(int)

# --- Filter to movies that have received votes (removes obscure entries) ---
meta['vote_count'] = pd.to_numeric(meta['vote_count'], errors='coerce').fillna(0)
meta = meta[meta['vote_count'] >= 25]
# Also filter out adult content
meta = meta[meta['adult'] != 'True']
# Only keep released movies
meta = meta[meta['status'] == 'Released']

print(f"Movies after quality filter (>=1 vote, released, non-adult): {len(meta)}")

# --- Merge all three datasets on ID ---
print("Merging datasets...")
movies = meta.merge(credits, on='id')
movies = movies.merge(keywords, on='id')

# Keep relevant columns
movies = movies[['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew', 'vote_count', 'vote_average', 'popularity']]
movies.dropna(subset=['title', 'overview'], inplace=True)
movies = movies.reset_index(drop=True)

print(f"After merge and cleanup: {len(movies)} movies")

# --- Helper functions ---
def safe_parse(text):
    """Safely parse JSON-like strings."""
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return []

def extract_names(text):
    """Extract 'name' field from JSON-like string."""
    return [item['name'] for item in safe_parse(text)]

def extract_top3_cast(text):
    """Extract top 3 cast member names."""
    parsed = safe_parse(text)
    return [item['name'] for item in parsed[:3]]

def extract_director(text):
    """Extract director name(s) from crew."""
    return [item['name'] for item in safe_parse(text) if item.get('job') == 'Director']

def collapse_spaces(word_list):
    """Remove spaces from multi-word entries."""
    return [w.replace(" ", "") for w in word_list]

# --- Process features ---
print("Processing features (this may take a minute)...")
movies['genres'] = movies['genres'].apply(extract_names)
movies['keywords'] = movies['keywords'].apply(extract_names)
movies['cast'] = movies['cast'].apply(extract_top3_cast)
movies['crew'] = movies['crew'].apply(extract_director)

# Collapse spaces so multi-word names are treated as single tokens
movies['genres'] = movies['genres'].apply(collapse_spaces)
movies['keywords'] = movies['keywords'].apply(collapse_spaces)
movies['cast'] = movies['cast'].apply(collapse_spaces)
movies['crew'] = movies['crew'].apply(collapse_spaces)

# Split overview into word lists
movies['overview'] = movies['overview'].apply(lambda x: x.split() if isinstance(x, str) else [])

# Create combined tags
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Build final dataframe
new = movies[['id', 'title', 'tags']].copy()
new.columns = ['movie_id', 'title', 'tags']
new['tags'] = new['tags'].apply(lambda x: " ".join(x).lower())

# Remove duplicate titles (keep most popular version)
new = new.drop_duplicates(subset='title', keep='first').reset_index(drop=True)

print(f"Final dataset: {len(new)} unique movies")

# --- Build similarity matrix ---
print("Building count vectors (max_features=5000)...")
cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(new['tags']).toarray()

print(f"Vector shape: {vector.shape}")
print("Computing cosine similarity matrix...")
similarity = cosine_similarity(vector)

# --- Save pickle files ---
os.makedirs(MODEL_DIR, exist_ok=True)

movie_list_path = os.path.join(MODEL_DIR, 'movie_list.pkl')
similarity_path = os.path.join(MODEL_DIR, 'similarity.pkl')

print(f"Saving model files to {MODEL_DIR}...")
pickle.dump(new, open(movie_list_path, 'wb'))
pickle.dump(similarity, open(similarity_path, 'wb'))

print(f"\nDone! Generated:")
print(f"  {movie_list_path} ({os.path.getsize(movie_list_path) / 1024 / 1024:.1f} MB)")
print(f"  {similarity_path} ({os.path.getsize(similarity_path) / 1024 / 1024:.1f} MB)")
print(f"  Total movies: {len(new)}")
