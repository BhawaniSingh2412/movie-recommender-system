import pickle
import streamlit as st
import requests
import json
import os
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    page_title="CineMatch — AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
USER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'user_data')
os.makedirs(USER_DATA_DIR, exist_ok=True)

# ─── CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.stApp { background: linear-gradient(160deg, #FAFBFE 0%, #EEF0FA 40%, #E8ECFA 100%); }

/* Hero */
.hero { text-align: center; padding: 1.5rem 1rem 0.5rem; }
.hero-icon { font-size: 2.5rem; display: inline-block; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
.hero h1 {
    font-size: 2.5rem; font-weight: 900;
    background: linear-gradient(135deg, #6C63FF, #4ECDC4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0.2rem 0; letter-spacing: -1.5px;
}
.hero p { font-size: 0.9rem; color: #6B7280; max-width: 500px; margin: 0 auto; }

/* Stats */
.stats { display:flex; justify-content:center; gap:2rem; margin:0.5rem 0 1rem; }
.stat { text-align:center; }
.stat-val { font-size:1.2rem; font-weight:700; color:#6C63FF; }
.stat-lbl { font-size:0.6rem; color:#9CA3AF; text-transform:uppercase; letter-spacing:1px; font-weight:600; }

/* Trending Section */
.trend-card {
    background: white; border-radius: 14px; overflow: hidden;
    box-shadow: 0 3px 15px rgba(108,99,255,0.06);
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    border: 1px solid rgba(108,99,255,0.04);
}
.trend-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 40px rgba(108,99,255,0.15);
}
.trend-card img { width:100%; aspect-ratio:2/3; object-fit:cover; display:block; transition:transform 0.5s; }
.trend-card:hover img { transform:scale(1.05); }
.trend-body { padding:0.5rem; }
.trend-title { font-size:0.75rem; font-weight:700; color:#1A1A2E; margin:0; line-height:1.2; display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }
.trend-meta { font-size:0.6rem; color:#9CA3AF; margin-top:0.15rem; }
.trend-rank {
    position:absolute; top:6px; left:6px; background:linear-gradient(135deg,#6C63FF,#4ECDC4);
    color:white; font-size:0.65rem; font-weight:800; padding:0.15rem 0.5rem; border-radius:20px;
}

/* Movie Card */
.movie-card {
    background:white; border-radius:16px; overflow:hidden;
    box-shadow:0 4px 20px rgba(108,99,255,0.07);
    transition:all 0.4s cubic-bezier(0.4,0,0.2,1);
    border:1px solid rgba(108,99,255,0.05);
}
.movie-card:hover {
    transform:translateY(-6px) scale(1.02);
    box-shadow:0 16px 48px rgba(108,99,255,0.18);
}
.poster-wrap { position:relative; overflow:hidden; }
.poster-wrap img { width:100%; aspect-ratio:2/3; object-fit:cover; display:block; transition:transform 0.5s; }
.movie-card:hover .poster-wrap img { transform:scale(1.05); }
.poster-overlay {
    position:absolute; bottom:0; left:0; right:0; padding:2rem 0.5rem 0.5rem;
    background:linear-gradient(transparent,rgba(0,0,0,0.85)); opacity:0; transition:opacity 0.3s;
}
.movie-card:hover .poster-overlay { opacity:1; }
.poster-overlay span { color:white; font-size:0.65rem; font-weight:600; background:rgba(108,99,255,0.9); padding:0.15rem 0.5rem; border-radius:20px; }
.card-body { padding:0.6rem; }
.card-title { font-size:0.78rem; font-weight:700; color:#1A1A2E; margin:0 0 0.2rem; line-height:1.2; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
.badge-row { display:flex; align-items:center; gap:0.25rem; flex-wrap:wrap; margin-bottom:0.25rem; }
.badge { font-size:0.55rem; font-weight:600; padding:0.1rem 0.4rem; border-radius:20px; }
.badge-genre { color:#6C63FF; background:rgba(108,99,255,0.08); }
.badge-year { color:#9CA3AF; background:#F3F4F6; }
.rating { font-size:0.65rem; font-weight:700; color:#F59E0B; }

/* Confidence */
.conf-wrap { margin-top:0.3rem; }
.conf-bar-bg { background:#F3F4F6; border-radius:10px; height:5px; overflow:hidden; }
.conf-bar-fill { height:100%; border-radius:10px; }
.conf-label { display:flex; justify-content:space-between; margin-top:0.15rem; }
.conf-text { font-size:0.55rem; color:#9CA3AF; font-weight:500; }
.conf-pct { font-size:0.65rem; font-weight:700; }

/* Explanation Card */
.explain-card {
    background: linear-gradient(135deg, #F8F7FF, #F0EEFF);
    border-radius: 12px; padding: 0.8rem; margin-top: 0.5rem;
    border-left: 3px solid #6C63FF;
}
.explain-title { font-size:0.75rem; font-weight:700; color:#1A1A2E; margin-bottom:0.3rem; }
.explain-reason { font-size:0.75rem; color:#4B5563; line-height:1.5; margin-bottom:0.2rem; }
.explain-tag { font-size:0.6rem; color:#6C63FF; font-weight:600; background:rgba(108,99,255,0.08); padding:0.1rem 0.4rem; border-radius:20px; display:inline-block; margin:0.1rem 0.1rem 0.1rem 0; }

/* Section */
.section-hdr { font-size:1.15rem; font-weight:700; color:#1A1A2E; margin:0.5rem 0 0.8rem; display:flex; align-items:center; gap:0.4rem; }
.divider { height:1px; background:linear-gradient(90deg,transparent,#D1D5DB,transparent); margin:0.8rem 0; }

/* Details */
.details-title { font-size:1.4rem; font-weight:800; color:#1A1A2E; margin:0 0 0.2rem; }
.details-tagline { font-size:0.8rem; color:#6C63FF; font-style:italic; margin-bottom:0.6rem; }
.details-overview { font-size:0.8rem; color:#4B5563; line-height:1.5; margin-bottom:0.6rem; }
.details-meta { display:flex; gap:1.2rem; flex-wrap:wrap; margin-bottom:0.6rem; }
.meta-item { text-align:center; }
.meta-val { font-size:1rem; font-weight:700; color:#1A1A2E; }
.meta-lbl { font-size:0.55rem; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.5px; }

/* Sidebar User */
.user-avatar { font-size:2.5rem; text-align:center; margin-bottom:0.3rem; }
.user-name { font-size:1.1rem; font-weight:700; color:#1A1A2E; text-align:center; margin-bottom:0.5rem; }
.user-stat { display:flex; justify-content:space-between; padding:0.3rem 0; border-bottom:1px solid #F3F4F6; font-size:0.8rem; }
.user-stat-lbl { color:#6B7280; }
.user-stat-val { font-weight:600; color:#1A1A2E; }

/* Streamlit Overrides */
.stTextInput > div > div > input {
    border-radius:12px !important; border:2px solid #E5E7EB !important; background:white !important;
    padding:0.55rem 0.8rem !important; font-size:0.9rem !important; transition:all 0.3s !important;
}
.stTextInput > div > div > input:focus { border-color:#6C63FF !important; box-shadow:0 0 0 3px rgba(108,99,255,0.1) !important; }
.stSelectbox > div > div { border-radius:12px !important; border:2px solid #E5E7EB !important; background:white !important; }
.stButton > button {
    background:linear-gradient(135deg,#6C63FF,#5B54E6) !important; color:white !important;
    border:none !important; border-radius:12px !important; padding:0.6rem 2rem !important;
    font-weight:700 !important; font-size:0.9rem !important; transition:all 0.3s !important;
    box-shadow:0 4px 18px rgba(108,99,255,0.3) !important; width:100% !important;
}
.stButton > button:hover { transform:translateY(-2px) !important; box-shadow:0 8px 30px rgba(108,99,255,0.4) !important; }

.footer { text-align:center; color:#9CA3AF; font-size:0.7rem; padding:1.5rem 0 0.5rem; }
.footer a { color:#6C63FF; text-decoration:none; font-weight:500; }

@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
.anim { animation:fadeUp 0.4s ease-out forwards; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───
@st.cache_resource
def load_data():
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# ─── User Profile System ───
def load_user(username):
    path = os.path.join(USER_DATA_DIR, f'{username}.json')
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {'name': username, 'history': [], 'favorites': [], 'created': datetime.now().isoformat()}

def save_user(username, data):
    path = os.path.join(USER_DATA_DIR, f'{username}.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# Init session state
if 'user' not in st.session_state:
    st.session_state.user = 'Guest'
if 'user_data' not in st.session_state:
    st.session_state.user_data = load_user('Guest')

# ─── Sidebar: User Profile ───
with st.sidebar:
    st.markdown('<div class="user-avatar">👤</div>', unsafe_allow_html=True)

    # User selector
    existing_users = [f.replace('.json', '') for f in os.listdir(USER_DATA_DIR) if f.endswith('.json')]
    if not existing_users:
        existing_users = ['Guest']

    new_user = st.text_input("🆕 Create new profile", placeholder="Enter username...")
    if new_user and new_user.strip():
        clean_name = new_user.strip()
        if clean_name not in existing_users:
            save_user(clean_name, {'name': clean_name, 'history': [], 'favorites': [], 'created': datetime.now().isoformat()})
            existing_users.append(clean_name)
            st.session_state.user = clean_name
            st.session_state.user_data = load_user(clean_name)
            st.rerun()

    selected_user = st.selectbox("👥 Switch profile", existing_users,
                                  index=existing_users.index(st.session_state.user) if st.session_state.user in existing_users else 0)
    if selected_user != st.session_state.user:
        st.session_state.user = selected_user
        st.session_state.user_data = load_user(selected_user)
        st.rerun()

    ud = st.session_state.user_data
    st.markdown(f'<div class="user-name">👋 {ud["name"]}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="user-stat"><span class="user-stat-lbl">🔍 Searches</span><span class="user-stat-val">{len(ud.get('history', []))}</span></div>
    <div class="user-stat"><span class="user-stat-lbl">❤️ Favorites</span><span class="user-stat-val">{len(ud.get('favorites', []))}</span></div>
    """, unsafe_allow_html=True)

    # Show recent history
    if ud.get('history'):
        st.markdown("**📜 Recent Searches**")
        for h in reversed(ud['history'][-5:]):
            st.caption(f"🎬 {h}")

    # Show favorites
    if ud.get('favorites'):
        st.markdown("**❤️ Favorites**")
        for f in ud['favorites'][-5:]:
            st.caption(f"⭐ {f}")


# ─── TMDB API ───
@st.cache_data(ttl=3600)
def fetch_trending():
    """Fetch today's trending movies from TMDB."""
    try:
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
        data = requests.get(url, timeout=8).json()
        results = []
        for m in data.get('results', [])[:10]:
            results.append({
                'title': m.get('title', ''),
                'poster': f"https://image.tmdb.org/t/p/w342{m['poster_path']}" if m.get('poster_path') else None,
                'rating': m.get('vote_average', 0),
                'year': m.get('release_date', '')[:4] if m.get('release_date') else '',
                'overview': m.get('overview', '')[:100] + '...',
            })
        return results
    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=videos,credits"
        data = requests.get(url, timeout=8).json()
        poster = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else None
        rating = data.get('vote_average', 0)
        vote_count = data.get('vote_count', 0)
        year = data.get('release_date', '')[:4] if data.get('release_date') else ''
        genres = [g['name'] for g in data.get('genres', [])[:3]]
        overview = data.get('overview', '')
        tagline = data.get('tagline', '')
        runtime = data.get('runtime', 0)
        budget = data.get('budget', 0)
        revenue = data.get('revenue', 0)
        trailer_key = None
        for v in data.get('videos', {}).get('results', []):
            if v.get('site') == 'YouTube' and v.get('type') == 'Trailer':
                trailer_key = v['key']
                break
        if not trailer_key:
            for v in data.get('videos', {}).get('results', []):
                if v.get('site') == 'YouTube':
                    trailer_key = v['key']
                    break
        cast = []
        for c in data.get('credits', {}).get('cast', [])[:5]:
            cast.append({'name': c['name'], 'character': c.get('character', ''),
                         'photo': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None})
        director = ''
        for c in data.get('credits', {}).get('crew', []):
            if c.get('job') == 'Director':
                director = c['name']
                break
        return {'poster': poster, 'rating': rating, 'vote_count': vote_count, 'year': year,
                'genres': genres, 'overview': overview, 'tagline': tagline, 'runtime': runtime,
                'budget': budget, 'revenue': revenue, 'trailer_key': trailer_key, 'cast': cast, 'director': director}
    except Exception:
        return None


def get_confidence_color(score):
    if score >= 70: return "linear-gradient(90deg,#10B981,#34D399)", "#10B981"
    elif score >= 50: return "linear-gradient(90deg,#6C63FF,#818CF8)", "#6C63FF"
    elif score >= 30: return "linear-gradient(90deg,#F59E0B,#FBBF24)", "#F59E0B"
    else: return "linear-gradient(90deg,#EF4444,#F87171)", "#EF4444"

def format_money(amt):
    if amt >= 1e9: return f"${amt/1e9:.1f}B"
    elif amt >= 1e6: return f"${amt/1e6:.0f}M"
    elif amt > 0: return f"${amt:,.0f}"
    return "—"


def generate_explanation(source_movie, rec_title, rec_details, match_score):
    """Generate a human-readable explanation for why a movie was recommended."""
    reasons = []
    source_lower = source_movie.lower()
    rec_lower = rec_title.lower()

    # Shared franchise/series
    source_words = set(source_lower.split())
    rec_words = set(rec_lower.split())
    common = source_words & rec_words - {'the', 'a', 'an', 'of', 'in', 'and', 'to', 'is'}
    if common:
        reasons.append(f"🎬 **Same franchise** — Both are part of the *{' '.join(w.title() for w in common)}* universe")

    # Shared genres
    if rec_details and rec_details.get('genres'):
        genres = rec_details['genres']
        reasons.append(f"🎭 **Genre match** — Shares the {', '.join(genres)} genre{'s' if len(genres)>1 else ''}")

    # Same director
    if rec_details and rec_details.get('director'):
        reasons.append(f"🎥 **Director** — Directed by {rec_details['director']}")

    # Confidence interpretation
    if match_score >= 75:
        reasons.append("🔥 **Very high similarity** — The plot, themes, and cast closely match your selection")
    elif match_score >= 60:
        reasons.append("✨ **Strong thematic overlap** — Similar storyline elements and narrative style")
    elif match_score >= 40:
        reasons.append("💡 **Shared themes** — Overlapping keywords and character archetypes")
    else:
        reasons.append("🌱 **Discovery pick** — May share subtle narrative or tonal similarities")

    # Era
    if rec_details and rec_details.get('year'):
        reasons.append(f"📅 Released in **{rec_details['year']}**")

    return reasons


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    results = []
    for i in distances[1:6]:
        mid = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        score = round(i[1] * 100)
        details = fetch_movie_details(mid)
        if details:
            details['title'] = title
            details['match'] = score
            details['explanations'] = generate_explanation(movie, title, details, score)
            results.append(details)
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HERO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(f"""
<div class="hero">
    <div class="hero-icon">🎬</div>
    <h1>CineMatch</h1>
    <p>AI-powered Netflix-level movie recommendations with deep learning</p>
</div>
""", unsafe_allow_html=True)

total_movies = len(movies)
st.markdown(f"""
<div class="stats">
    <div class="stat"><div class="stat-val">{total_movies:,}</div><div class="stat-lbl">Movies</div></div>
    <div class="stat"><div class="stat-val">🧠</div><div class="stat-lbl">Deep Learning</div></div>
    <div class="stat"><div class="stat-val">🎥</div><div class="stat-lbl">Trailers</div></div>
    <div class="stat"><div class="stat-val">👤</div><div class="stat-lbl">{st.session_state.user}</div></div>
</div>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 TRENDING NOW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown('<div class="section-hdr">🎯 Trending Today</div>', unsafe_allow_html=True)

trending = fetch_trending()
if trending:
    tcols = st.columns(min(10, len(trending)), gap="small")
    for i, (tc, tm) in enumerate(zip(tcols, trending)):
        with tc:
            poster_url = tm['poster'] or "https://via.placeholder.com/342x513/1A1A2E/6C63FF?text=N/A"
            st.markdown(f"""
            <div class="trend-card anim" style="position:relative; animation-delay:{i*0.05}s">
                <div class="trend-rank">#{i+1}</div>
                <img src="{poster_url}" loading="lazy"/>
                <div class="trend-body">
                    <div class="trend-title">{tm['title']}</div>
                    <div class="trend-meta">⭐ {tm['rating']:.1f} · {tm['year']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 SEARCH (Real-time)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
movie_list = sorted(movies['title'].values.tolist())

col_l, col_c, col_r = st.columns([1, 3, 1])
with col_c:
    search_query = st.text_input("🔍 Search for a movie", placeholder="Type a movie name...", key="search")

    if search_query:
        q = search_query.lower().strip()
        exact = [m for m in movie_list if m.lower() == q]
        starts = [m for m in movie_list if m.lower().startswith(q) and m.lower() != q]
        contains = [m for m in movie_list if q in m.lower() and not m.lower().startswith(q)]
        filtered = exact + starts + contains
        if filtered:
            selected_movie = st.selectbox(f"🎯 {len(filtered)} movie(s) found", filtered, index=0)
        else:
            st.warning(f"❌ No movies matching **\"{search_query}\"**")
            selected_movie = None
    else:
        selected_movie = st.selectbox("Browse catalog", movie_list, index=None, placeholder="Or browse all movies...")

    show_btn = st.button("✨ Get Recommendations", use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔥 RECOMMENDATIONS (with explanations)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if show_btn and selected_movie:
    # Save to user history
    ud = st.session_state.user_data
    if selected_movie not in ud.get('history', []):
        ud.setdefault('history', []).append(selected_movie)
        save_user(st.session_state.user, ud)

    with st.spinner("🧠 AI is analyzing deep semantic similarities..."):
        results = recommend(selected_movie)

    st.markdown(f'<div class="section-hdr">🔥 Because you loved <em style="color:#6C63FF">{selected_movie}</em></div>', unsafe_allow_html=True)

    # Movie cards
    cols = st.columns(5, gap="medium")
    for idx, (col, m) in enumerate(zip(cols, results)):
        with col:
            poster_url = m['poster'] or "https://via.placeholder.com/500x750/1A1A2E/6C63FF?text=No+Poster"
            stars = "⭐" * max(1, round(m['rating']/2))
            genre_badges = "".join([f'<span class="badge badge-genre">{g}</span>' for g in m.get('genres', [])])
            year_badge = f'<span class="badge badge-year">{m["year"]}</span>' if m.get('year') else ''
            grad, color = get_confidence_color(m['match'])

            st.markdown(f"""
            <div class="movie-card anim" style="animation-delay:{idx*0.1}s">
                <div class="poster-wrap">
                    <img src="{poster_url}" alt="{m['title']}" loading="lazy"/>
                    <div class="poster-overlay"><span>{'🎥 Trailer' if m.get('trailer_key') else '📋 Details'}</span></div>
                </div>
                <div class="card-body">
                    <div class="card-title">{m['title']}</div>
                    <div class="badge-row"><span class="rating">{stars} {m['rating']:.1f}</span></div>
                    <div class="badge-row">{genre_badges} {year_badge}</div>
                    <div class="conf-wrap">
                        <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{m['match']}%;background:{grad};"></div></div>
                        <div class="conf-label">
                            <span class="conf-text">Confidence</span>
                            <span class="conf-pct" style="color:{color}">{m['match']}%</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Favorite button
            fav_key = f"fav_{idx}_{m['title']}"
            is_fav = m['title'] in ud.get('favorites', [])
            if st.button("❤️" if is_fav else "🤍", key=fav_key, use_container_width=True):
                if is_fav:
                    ud['favorites'].remove(m['title'])
                else:
                    ud.setdefault('favorites', []).append(m['title'])
                save_user(st.session_state.user, ud)
                st.rerun()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Detailed views with explanations ──
    for idx, m in enumerate(results):
        with st.expander(f"🎬 {m['title']} — {m['match']}% match", expanded=(idx == 0)):

            # 📊 EXPLANATION CARD (top of details)
            explain_html = ""
            for reason in m.get('explanations', []):
                explain_html += f'<div class="explain-reason">{reason}</div>'
            st.markdown(f"""
            <div class="explain-card">
                <div class="explain-title">📊 Why this was recommended</div>
                {explain_html}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("")  # spacing

            det_l, det_r = st.columns([1, 2])
            with det_l:
                if m['poster']:
                    st.image(m['poster'], use_container_width=True)

            with det_r:
                st.markdown(f'<div class="details-title">{m["title"]}</div>', unsafe_allow_html=True)
                if m['tagline']:
                    st.markdown(f'<div class="details-tagline">"{m["tagline"]}"</div>', unsafe_allow_html=True)

                runtime_str = f"{m['runtime']}min" if m['runtime'] else "—"
                meta_html = f"""<div class="details-meta">
                    <div class="meta-item"><div class="meta-val">⭐ {m['rating']:.1f}</div><div class="meta-lbl">{m['vote_count']:,} votes</div></div>
                    <div class="meta-item"><div class="meta-val">🕐 {runtime_str}</div><div class="meta-lbl">Runtime</div></div>
                    <div class="meta-item"><div class="meta-val">📅 {m['year']}</div><div class="meta-lbl">Year</div></div>"""
                if m['budget']: meta_html += f'<div class="meta-item"><div class="meta-val">💰 {format_money(m["budget"])}</div><div class="meta-lbl">Budget</div></div>'
                if m['revenue']: meta_html += f'<div class="meta-item"><div class="meta-val">💵 {format_money(m["revenue"])}</div><div class="meta-lbl">Revenue</div></div>'
                meta_html += "</div>"
                st.markdown(meta_html, unsafe_allow_html=True)

                grad, color = get_confidence_color(m['match'])
                st.markdown(f"""
                <div style="margin-bottom:0.6rem">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.15rem">
                        <span style="font-size:0.7rem;font-weight:600;color:#4B5563">Recommendation Confidence</span>
                        <span style="font-size:1rem;font-weight:800;color:{color}">{m['match']}%</span>
                    </div>
                    <div style="background:#F3F4F6;border-radius:10px;height:8px;overflow:hidden">
                        <div style="background:{grad};width:{m['match']}%;height:100%;border-radius:10px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if m['overview']:
                    st.markdown(f'<div class="details-overview">{m["overview"]}</div>', unsafe_allow_html=True)
                if m['genres']:
                    st.markdown(" ".join([f'<span class="badge badge-genre" style="font-size:0.7rem;padding:0.15rem 0.5rem">{g}</span>' for g in m['genres']]), unsafe_allow_html=True)
                if m['director']:
                    st.markdown(f"**🎬 Director:** {m['director']}")

            if m['cast']:
                st.markdown("**🎭 Top Cast**")
                cast_cols = st.columns(min(5, len(m['cast'])))
                for cc, actor in zip(cast_cols, m['cast']):
                    with cc:
                        if actor['photo']:
                            st.image(actor['photo'], width=80)
                        st.caption(f"**{actor['name']}**\n{actor['character']}")

            if m.get('trailer_key'):
                st.markdown("**🎥 Watch Trailer**")
                st.video(f"https://www.youtube.com/watch?v={m['trailer_key']}")
            else:
                st.info("🎬 No trailer available")

elif show_btn and not selected_movie:
    st.warning("🎬 Please select a movie first!")

# ── Personalized Picks (based on user history) ──
ud = st.session_state.user_data
if ud.get('history') and not show_btn:
    last_movie = ud['history'][-1]
    if last_movie in movies['title'].values:
        st.markdown(f'<div class="section-hdr">🔥 Your Personalized Picks (based on <em style="color:#6C63FF">{last_movie}</em>)</div>', unsafe_allow_html=True)
        with st.spinner("Loading your picks..."):
            personal_results = recommend(last_movie)
        p_cols = st.columns(5, gap="medium")
        for idx, (col, m) in enumerate(zip(p_cols, personal_results)):
            with col:
                poster_url = m['poster'] or "https://via.placeholder.com/500x750/1A1A2E/6C63FF?text=N/A"
                grad, color = get_confidence_color(m['match'])
                st.markdown(f"""
                <div class="movie-card anim" style="animation-delay:{idx*0.08}s">
                    <div class="poster-wrap"><img src="{poster_url}" loading="lazy"/></div>
                    <div class="card-body">
                        <div class="card-title">{m['title']}</div>
                        <div class="badge-row"><span class="rating">⭐ {m['rating']:.1f}</span></div>
                        <div class="conf-wrap">
                            <div class="conf-bar-bg"><div class="conf-bar-fill" style="width:{m['match']}%;background:{grad}"></div></div>
                            <div class="conf-label"><span class="conf-text">Match</span><span class="conf-pct" style="color:{color}">{m['match']}%</span></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Built with ❤️ using <strong>Streamlit</strong> · Deep Learning with <strong>Sentence Transformers</strong>
    <br/>13,000+ movies · <a href="https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset">The Movies Dataset</a>
    · <a href="https://www.themoviedb.org/">TMDB</a>
</div>
""", unsafe_allow_html=True)
