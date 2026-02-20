import pickle
import streamlit as st
import requests

# ─── Page Config ───
st.set_page_config(
    page_title="CineMatch — AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.stApp {
    background: linear-gradient(160deg, #FAFBFE 0%, #EEF0FA 40%, #E8ECFA 100%);
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 2rem 1rem 1rem;
}
.hero-icon {
    font-size: 2.8rem;
    display: inline-block;
    animation: float 3s ease-in-out infinite;
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
.hero h1 {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0.2rem 0;
    letter-spacing: -1.5px;
}
.hero p {
    font-size: 1rem;
    color: #6B7280;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.5;
}

/* ── Stats ── */
.stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 0.8rem 0 1.5rem;
}
.stat { text-align: center; }
.stat-val {
    font-size: 1.3rem;
    font-weight: 700;
    color: #6C63FF;
}
.stat-lbl {
    font-size: 0.65rem;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

/* ── Movie Card ── */
.movie-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(108, 99, 255, 0.07);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(108, 99, 255, 0.05);
    margin-bottom: 0.5rem;
}
.movie-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 16px 48px rgba(108, 99, 255, 0.18);
    border-color: rgba(108, 99, 255, 0.15);
}
.poster-wrap {
    position: relative;
    overflow: hidden;
}
.poster-wrap img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
    transition: transform 0.5s ease;
}
.movie-card:hover .poster-wrap img {
    transform: scale(1.05);
}
.poster-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 2rem 0.6rem 0.6rem;
    background: linear-gradient(transparent, rgba(0,0,0,0.85));
    opacity: 0;
    transition: opacity 0.3s ease;
}
.movie-card:hover .poster-overlay {
    opacity: 1;
}
.poster-overlay span {
    color: white;
    font-size: 0.7rem;
    font-weight: 600;
    background: rgba(108, 99, 255, 0.9);
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
}
.card-body {
    padding: 0.7rem 0.7rem 0.5rem;
}
.card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 0 0 0.3rem;
    line-height: 1.25;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.badge-row {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    flex-wrap: wrap;
    margin-bottom: 0.35rem;
}
.badge {
    font-size: 0.6rem;
    font-weight: 600;
    padding: 0.12rem 0.45rem;
    border-radius: 20px;
}
.badge-genre {
    color: #6C63FF;
    background: rgba(108, 99, 255, 0.08);
}
.badge-year {
    color: #9CA3AF;
    background: #F3F4F6;
}
.rating {
    font-size: 0.7rem;
    font-weight: 700;
    color: #F59E0B;
}

/* ── Confidence Bar ── */
.conf-wrap {
    margin-top: 0.4rem;
}
.conf-bar-bg {
    background: #F3F4F6;
    border-radius: 10px;
    height: 6px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 1s ease-out;
}
.conf-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 0.2rem;
}
.conf-text {
    font-size: 0.6rem;
    color: #9CA3AF;
    font-weight: 500;
}
.conf-pct {
    font-size: 0.7rem;
    font-weight: 700;
}

/* ── Details Panel ── */
.details-panel {
    background: white;
    border-radius: 16px;
    padding: 1.2rem;
    box-shadow: 0 4px 20px rgba(108, 99, 255, 0.08);
    margin-top: 0.5rem;
    border: 1px solid rgba(108, 99, 255, 0.06);
}
.details-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #1A1A2E;
    margin: 0 0 0.3rem;
}
.details-tagline {
    font-size: 0.85rem;
    color: #6C63FF;
    font-style: italic;
    margin-bottom: 0.8rem;
}
.details-overview {
    font-size: 0.85rem;
    color: #4B5563;
    line-height: 1.6;
    margin-bottom: 0.8rem;
}
.details-meta {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.8rem;
}
.meta-item {
    text-align: center;
}
.meta-val {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1A1A2E;
}
.meta-lbl {
    font-size: 0.6rem;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ── Section Header ── */
.section-hdr {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 0.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Streamlit Overrides ── */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    background: white !important;
    padding: 0.6rem 0.8rem !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1) !important;
}
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    background: white !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #5B54E6) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.65rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 18px rgba(108, 99, 255, 0.3) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(108, 99, 255, 0.4) !important;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #D1D5DB, transparent);
    margin: 0.8rem 0 1rem;
}

.footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.75rem;
    padding: 2rem 0 1rem;
    margin-top: 1.5rem;
}
.footer a { color: #6C63FF; text-decoration: none; font-weight: 500; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}
.anim { animation: fadeUp 0.5s ease-out forwards; }

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
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


# ─── TMDB API Helpers ───
@st.cache_data(ttl=3600)
def fetch_movie_details(movie_id):
    """Fetch full movie details from TMDB."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=videos,credits"
        data = requests.get(url, timeout=8).json()

        poster = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else None
        backdrop = f"https://image.tmdb.org/t/p/w1280{data['backdrop_path']}" if data.get('backdrop_path') else None
        rating = data.get('vote_average', 0)
        vote_count = data.get('vote_count', 0)
        year = data.get('release_date', '')[:4] if data.get('release_date') else ''
        genres = [g['name'] for g in data.get('genres', [])[:3]]
        overview = data.get('overview', '')
        tagline = data.get('tagline', '')
        runtime = data.get('runtime', 0)
        budget = data.get('budget', 0)
        revenue = data.get('revenue', 0)

        # Get YouTube trailer
        trailer_key = None
        videos = data.get('videos', {}).get('results', [])
        for v in videos:
            if v.get('site') == 'YouTube' and v.get('type') == 'Trailer':
                trailer_key = v['key']
                break
        if not trailer_key:
            for v in videos:
                if v.get('site') == 'YouTube':
                    trailer_key = v['key']
                    break

        # Get top cast
        cast = []
        for c in data.get('credits', {}).get('cast', [])[:5]:
            cast.append({
                'name': c['name'],
                'character': c.get('character', ''),
                'photo': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else None,
            })

        # Get director
        director = ''
        for c in data.get('credits', {}).get('crew', []):
            if c.get('job') == 'Director':
                director = c['name']
                break

        return {
            'poster': poster,
            'backdrop': backdrop,
            'rating': rating,
            'vote_count': vote_count,
            'year': year,
            'genres': genres,
            'overview': overview,
            'tagline': tagline,
            'runtime': runtime,
            'budget': budget,
            'revenue': revenue,
            'trailer_key': trailer_key,
            'cast': cast,
            'director': director,
        }
    except Exception:
        return None


def get_confidence_color(score):
    """Return gradient color based on confidence score."""
    if score >= 70:
        return "linear-gradient(90deg, #10B981, #34D399)", "#10B981"
    elif score >= 50:
        return "linear-gradient(90deg, #6C63FF, #818CF8)", "#6C63FF"
    elif score >= 30:
        return "linear-gradient(90deg, #F59E0B, #FBBF24)", "#F59E0B"
    else:
        return "linear-gradient(90deg, #EF4444, #F87171)", "#EF4444"


def format_money(amount):
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.0f}M"
    elif amount > 0:
        return f"${amount:,.0f}"
    return "—"


def recommend(movie):
    """Get top 5 recommendations."""
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    results = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        score = round(i[1] * 100)
        details = fetch_movie_details(movie_id)
        if details:
            details['title'] = title
            details['match'] = score
            results.append(details)
    return results


# ─── Hero ───
st.markdown("""
<div class="hero">
    <div class="hero-icon">🎬</div>
    <h1>CineMatch</h1>
    <p>AI-powered movie recommendations with trailers, details & deep learning similarity</p>
</div>
""", unsafe_allow_html=True)

total_movies = len(movies)
st.markdown(f"""
<div class="stats">
    <div class="stat"><div class="stat-val">{total_movies:,}</div><div class="stat-lbl">Movies</div></div>
    <div class="stat"><div class="stat-val">🧠</div><div class="stat-lbl">Deep Learning</div></div>
    <div class="stat"><div class="stat-val">🎥</div><div class="stat-lbl">Trailers</div></div>
</div>
""", unsafe_allow_html=True)


# ─── Search ───
movie_list = sorted(movies['title'].values.tolist())

col_l, col_c, col_r = st.columns([1, 3, 1])
with col_c:
    search_query = st.text_input(
        "🔍  Search for a movie",
        placeholder="Type a movie name... e.g. Inception, Titanic, The Dark Knight",
        key="search",
    )

    if search_query:
        q = search_query.lower().strip()
        exact = [m for m in movie_list if m.lower() == q]
        starts = [m for m in movie_list if m.lower().startswith(q) and m.lower() != q]
        contains = [m for m in movie_list if q in m.lower() and not m.lower().startswith(q)]
        filtered = exact + starts + contains

        if filtered:
            selected_movie = st.selectbox(
                f"🎯  {len(filtered)} movie(s) found",
                filtered, index=0,
            )
        else:
            st.warning(f"❌ No movies found matching **\"{search_query}\"**")
            selected_movie = None
    else:
        selected_movie = st.selectbox(
            "Browse all movies",
            movie_list, index=None,
            placeholder="Or browse the full catalog...",
        )

    show_btn = st.button("✨  Get Recommendations", use_container_width=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ─── Recommendations ───
if show_btn and selected_movie:
    with st.spinner("🧠 Deep learning engine analyzing similarities..."):
        results = recommend(selected_movie)

    st.markdown(f"""
    <div class="section-hdr">
        🍿 Because you loved <em style="color:#6C63FF">{selected_movie}</em>
    </div>
    """, unsafe_allow_html=True)

    # ── Movie Cards Row ──
    cols = st.columns(5, gap="medium")
    for idx, (col, m) in enumerate(zip(cols, results)):
        with col:
            poster_url = m['poster'] or "https://via.placeholder.com/500x750/1A1A2E/6C63FF?text=No+Poster"
            stars = "⭐" * max(1, round(m['rating'] / 2))
            genre_badges = "".join([f'<span class="badge badge-genre">{g}</span>' for g in m['genres']])
            year_badge = f'<span class="badge badge-year">{m["year"]}</span>' if m['year'] else ''
            grad, color = get_confidence_color(m['match'])

            st.markdown(f"""
            <div class="movie-card anim" style="animation-delay:{idx*0.1}s">
                <div class="poster-wrap">
                    <img src="{poster_url}" alt="{m['title']}" loading="lazy"/>
                    <div class="poster-overlay">
                        <span>{'🎬 Trailer' if m.get('trailer_key') else '📽️ Details'}</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="card-title">{m['title']}</div>
                    <div class="badge-row">
                        <span class="rating">{stars} {m['rating']:.1f}</span>
                    </div>
                    <div class="badge-row">
                        {genre_badges} {year_badge}
                    </div>
                    <div class="conf-wrap">
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill" style="width:{m['match']}%; background:{grad};"></div>
                        </div>
                        <div class="conf-label">
                            <span class="conf-text">Confidence</span>
                            <span class="conf-pct" style="color:{color}">{m['match']}%</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Detailed Movie Views ──
    for idx, m in enumerate(results):
        with st.expander(f"🎬  {m['title']}  —  {m['match']}% match", expanded=(idx == 0)):
            det_left, det_right = st.columns([1, 2])

            with det_left:
                if m['poster']:
                    st.image(m['poster'], use_container_width=True)

            with det_right:
                # Title + tagline
                st.markdown(f'<div class="details-title">{m["title"]}</div>', unsafe_allow_html=True)
                if m['tagline']:
                    st.markdown(f'<div class="details-tagline">"{m["tagline"]}"</div>', unsafe_allow_html=True)

                # Meta stats
                runtime_str = f"{m['runtime']}min" if m['runtime'] else "—"
                meta_html = f"""
                <div class="details-meta">
                    <div class="meta-item"><div class="meta-val">⭐ {m['rating']:.1f}</div><div class="meta-lbl">{m['vote_count']:,} votes</div></div>
                    <div class="meta-item"><div class="meta-val">🕐 {runtime_str}</div><div class="meta-lbl">Runtime</div></div>
                    <div class="meta-item"><div class="meta-val">📅 {m['year']}</div><div class="meta-lbl">Year</div></div>
                """
                if m['budget']:
                    meta_html += f'<div class="meta-item"><div class="meta-val">💰 {format_money(m["budget"])}</div><div class="meta-lbl">Budget</div></div>'
                if m['revenue']:
                    meta_html += f'<div class="meta-item"><div class="meta-val">💵 {format_money(m["revenue"])}</div><div class="meta-lbl">Revenue</div></div>'
                meta_html += "</div>"
                st.markdown(meta_html, unsafe_allow_html=True)

                # Confidence score
                grad, color = get_confidence_color(m['match'])
                st.markdown(f"""
                <div style="margin-bottom: 0.8rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.2rem;">
                        <span style="font-size:0.75rem; font-weight:600; color:#4B5563;">Recommendation Confidence</span>
                        <span style="font-size:1rem; font-weight:800; color:{color};">{m['match']}%</span>
                    </div>
                    <div style="background:#F3F4F6; border-radius:10px; height:8px; overflow:hidden;">
                        <div style="background:{grad}; width:{m['match']}%; height:100%; border-radius:10px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Overview
                if m['overview']:
                    st.markdown(f'<div class="details-overview">{m["overview"]}</div>', unsafe_allow_html=True)

                # Genres + Director
                if m['genres']:
                    genre_html = " ".join([f'<span class="badge badge-genre" style="font-size:0.75rem; padding:0.2rem 0.6rem;">{g}</span>' for g in m['genres']])
                    st.markdown(f'<div style="margin-bottom:0.5rem;">{genre_html}</div>', unsafe_allow_html=True)

                if m['director']:
                    st.markdown(f"**🎬 Director:** {m['director']}")

            # Cast
            if m['cast']:
                st.markdown("**🎭 Top Cast**")
                cast_cols = st.columns(min(5, len(m['cast'])))
                for ci, (cc, actor) in enumerate(zip(cast_cols, m['cast'])):
                    with cc:
                        if actor['photo']:
                            st.image(actor['photo'], width=80)
                        st.caption(f"**{actor['name']}**\n{actor['character']}")

            # YouTube Trailer
            if m.get('trailer_key'):
                st.markdown("**🎥 Watch Trailer**")
                st.video(f"https://www.youtube.com/watch?v={m['trailer_key']}")
            else:
                st.info("🎬 No trailer available for this title")

elif show_btn and not selected_movie:
    st.warning("🎬 Please select a movie first!")


# ─── Footer ───
st.markdown("""
<div class="footer">
    Built with ❤️ using <strong>Streamlit</strong> &middot; Deep Learning with <strong>Sentence Transformers</strong>
    <br/>
    13,000+ movies from <a href="https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset">The Movies Dataset</a>
    &middot; Trailers & data from <a href="https://www.themoviedb.org/">TMDB</a>
</div>
""", unsafe_allow_html=True)
