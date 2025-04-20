import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

st.set_page_config(page_title="프리사운드 효과음 검색기", layout="wide")

st.markdown("""
<style>
    .main-header { font-size: 2rem; color: #1E3A8A; text-align: center; font-weight: bold; margin-bottom: 0.5rem; }
    .sound-card { background: white; border-left: 4px solid #2563EB; padding: 10px; margin-bottom: 10px; border-radius: 8px; }
    .sound-title { font-size: 1.1rem; font-weight: bold; color: #1E3A8A; }
    .button-primary, .button-secondary { padding: 4px 10px; border-radius: 5px; text-decoration: none; font-size: 0.85rem; }
    .button-primary { background-color: #2563EB; color: white; }
    .button-secondary { background-color: #10B981; color: white; }
    audio { width: 100%; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🎵 프리사운드 효과음 검색기</h1>', unsafe_allow_html=True)


def search_freesound(query):
    url = f"https://freesound.org/search/?q={quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".bw-search__result")

    results = []
    for item in items[:10]:
        name_elem = item.select_one(".title a")
        if not name_elem:
            continue
        name = name_elem.text.strip()
        link = name_elem['href']
        sound_id = link.split('/')[2] if '/sounds/' in link else ''
        preview = f"https://freesound.org/data/previews/{sound_id[:3]}/{sound_id}/previews-hq-{sound_id}-HQ.mp3"
        results.append({
            'name': name,
            'url': f"https://freesound.org{link}",
            'preview': preview
        })
    return results

query = st.text_input("효과음을 검색해보세요 (예: rain, bell)")
if st.button("검색") and query:
    with st.spinner("🔍 검색 중..."):
        sounds = search_freesound(query)
        if not sounds:
            st.info("결과가 없습니다. 영어로 검색해보세요.")
        for sound in sounds:
            st.markdown(f"""
            <div class='sound-card'>
                <div class='sound-title'>{sound['name']}</div>
                <audio controls><source src="{sound['preview']}" type="audio/mpeg"></audio>
                <a href="{sound['url']}" target="_blank" class="button-primary">상세정보/다운로드</a>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<div style="text-align:center; margin-top:20px; font-size:0.9rem;">🔊 Freesound.org의 효과음을 검색합니다</div>', unsafe_allow_html=True)
