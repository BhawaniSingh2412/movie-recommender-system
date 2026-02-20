import pickle
import streamlit as st
import requests

# ─── Page Config ───
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Global background ── */
.stApp {
    background: linear-gradient(135deg, #FAFBFE 0%, #F0F2FA 50%, #E8ECFA 100%);
}

/* ── Hero Section ── */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    margin-bottom: 0.5rem;
}
.hero-icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    display: inline-block;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #4ECDC4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.4rem 0;
    letter-spacing: -1px;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #6B7280;
    font-weight: 400;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.5;
}

/* ── Search Section ── */
.search-section {
    max-width: 680px;
    margin: 1rem auto 2rem;
    padding: 0 1rem;
}

/* ── Stats Bar ── */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin: 1rem auto 2rem;
    padding: 0.8rem 0;
}
.stat-item {
    text-align: center;
}
.stat-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: #6C63FF;
}
.stat-label {
    font-size: 0.75rem;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}

/* ── Section Headers ── */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 0 0 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header span {
    font-size: 1.2rem;
}

/* ── Movie Cards ── */
.movie-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(108, 99, 255, 0.08);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border: 1px solid rgba(108, 99, 255, 0.06);
    height: 100%;
}
.movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(108, 99, 255, 0.18);
    border-color: rgba(108, 99, 255, 0.2);
}
.movie-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
}
.card-body {
    padding: 0.8rem;
}
.card-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #1A1A2E;
    margin: 0 0 0.25rem 0;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.card-meta {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-wrap: wrap;
}
.card-badge {
    font-size: 0.65rem;
    font-weight: 500;
    color: #6C63FF;
    background: rgba(108, 99, 255, 0.08);
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
}
.card-rating {
    font-size: 0.7rem;
    color: #F59E0B;
    font-weight: 600;
}

/* ── Streamlit Overrides ── */
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    background: white !important;
    padding: 0.15rem !important;
    transition: border-color 0.3s ease !important;
}
.stSelectbox > div > div:focus-within {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #5B54E6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(108, 99, 255, 0.25) !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #5B54E6, #4A44CC) !important;
    box-shadow: 0 6px 25px rgba(108, 99, 255, 0.35) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #D1D5DB, transparent);
    margin: 1rem 0 1.5rem;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.8rem;
    padding: 2rem 0 1rem;
    margin-top: 2rem;
}
.footer a {
    color: #6C63FF;
    text-decoration: none;
    font-weight: 500;
}

/* ── Powered by badge ── */
.powered-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(108, 99, 255, 0.06);
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.7rem;
    color: #6B7280;
    margin-top: 0.5rem;
}

/* ── Animation ── */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.animate-in {
    animation: fadeInUp 0.5s ease-out forwards;
}
</style>
""", unsafe_allow_html=True)


# ─── Load Data ───
@st.cache_resource
def load_data():
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()


# ─── API Functions ───
def fetch_movie_details(movie_id):
    """Fetch poster, rating, year, and genres from TMDB."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url, timeout=5).json()
        poster = f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}" if data.get('poster_path') else None
        rating = data.get('vote_average', 0)
        year = data.get('release_date', '')[:4] if data.get('release_date') else ''
        genres = [g['name'] for g in data.get('genres', [])[:2]]
        return poster, rating, year, genres
    except Exception:
        return None, 0, '', []


def recommend(movie):
    """Get top 5 recommended movies with details."""
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommendations = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        score = round(i[1] * 100)
        poster, rating, year, genres = fetch_movie_details(movie_id)
        recommendations.append({
            'title': title,
            'poster': poster,
            'rating': rating,
            'year': year,
            'genres': genres,
            'match': score,
        })
    return recommendations


# ─── Hero Section ───
st.markdown("""
<div class="hero-container">
    <div class="hero-icon">🎬</div>
    <h1 class="hero-title">CineMatch</h1>
    <p class="hero-subtitle">Discover your next favorite movie with AI-powered recommendations from 13,000+ films</p>
</div>
""", unsafe_allow_html=True)

# ─── Stats Bar ───
total_movies = len(movies)
st.markdown(f"""
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-number">{total_movies:,}</div>
        <div class="stat-label">Movies</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">5</div>
        <div class="stat-label">Top Picks</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">AI</div>
        <div class="stat-label">Powered</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Search Section ───
movie_list = movies['title'].values

col_left, col_center, col_right = st.columns([1, 3, 1])
with col_center:
    selected_movie = st.selectbox(
        "🔍  Search for a movie",
        movie_list,
        index=None,
        placeholder="Type a movie name... e.g. Inception, Titanic, Avatar",
    )

    show_btn = st.button("✨  Get Recommendations", use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ─── Recommendations ───
if show_btn and selected_movie:
    with st.spinner("🎥 Finding perfect matches..."):
        results = recommend(selected_movie)

    st.markdown(f"""
    <div class="section-header">
        <span>🍿</span> Because you liked <em style="color: #6C63FF;">{selected_movie}</em>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5, gap="medium")
    for idx, (col, movie) in enumerate(zip(cols, results)):
        with col:
            poster_url = movie['poster'] or "https://via.placeholder.com/500x750?text=No+Poster"
            rating_stars = "⭐" * max(1, round(movie['rating'] / 2))
            genre_badges = "".join([f'<span class="card-badge">{g}</span>' for g in movie['genres']])
            match_pct = movie['match']

            st.markdown(f"""
            <div class="movie-card animate-in" style="animation-delay: {idx * 0.1}s">
                <img src="{poster_url}" alt="{movie['title']}" loading="lazy"/>
                <div class="card-body">
                    <div class="card-title">{movie['title']}</div>
                    <div class="card-meta">
                        <span class="card-rating">{rating_stars} {movie['rating']:.1f}</span>
                    </div>
                    <div class="card-meta" style="margin-top: 0.3rem;">
                        {genre_badges}
                        {f'<span class="card-badge" style="color:#9CA3AF">{movie["year"]}</span>' if movie['year'] else ''}
                    </div>
                    <div style="margin-top: 0.4rem;">
                        <div style="background: #F3F4F6; border-radius: 10px; height: 4px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #6C63FF, #4ECDC4); width: {match_pct}%; height: 100%; border-radius: 10px;"></div>
                        </div>
                        <div style="font-size: 0.65rem; color: #9CA3AF; margin-top: 0.15rem; font-weight: 500;">{match_pct}% match</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif show_btn and not selected_movie:
    st.warning("🎬 Please select a movie first!")

# ─── Footer ───
st.markdown("""
<div class="footer">
    <div class="powered-badge">🤖 Powered by Cosine Similarity & TMDB API</div>
    <br/>
    Built with ❤️ using Streamlit &middot; 13,000+ movies from <a href="https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset" target="_blank">The Movies Dataset</a>
</div>
""", unsafe_allow_html=True)
