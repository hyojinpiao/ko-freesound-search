import streamlit as st
import requests

API_KEY = "6xbTcaH4kDOXvKTCg8NJqZCTVKiRgGZI0C5S0hFX"

def search_freesound_api(query):
    url = (
        f"https://freesound.org/apiv2/search/text/"
        f"?query={query}&fields=name,id,previews&token={API_KEY}"
        f"&sort=downloads_desc&page_size=5"
    )
    res = requests.get(url)

    if res.status_code != 200:
        st.error("API 요청 실패 😢")
        return []

    data = res.json()
    results = []
    for sound in data.get("results", []):
        preview = sound.get("previews", {}).get("preview-hq-mp3")
        if preview:
            results.append({
                "name": sound.get("name", "제목 없음"),
                "preview": preview,
                "url": f"https://freesound.org/s/{sound['id']}/"
            })
    return results

# 페이지 구성
st.set_page_config(page_title="효과음 검색기", layout="centered")

# 스타일 설정
st.markdown("""
<style>
h1, h2, h3 {
    text-align: center;
    font-size: 1rem !important; /* 타이틀 크기를 1rem으로 변경 */
}
.sound-title {
    font-size: 1rem;
    font-weight: bold;
    margin-bottom: 0.2rem;
}
.download-link {
    font-size: 0.9rem;
    color: #2563eb;
    margin-top: 0.3rem;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# UI 헤더
st.markdown("### 🔍 Freesound 효과음 검색기")

# 검색창
query = st.text_input("효과음을 검색하세요", placeholder="(영어로 검색하세요)") # placeholder 추가

if st.button("검색") and query:
    with st.spinner("검색 중..."):
        results = search_freesound_api(query)
        if not results:
            st.warning("결과가 없습니다. 영어로 검색해보세요.")
        for r in results:
            st.markdown(f"<div class='sound-title'>🎵 {r['name']}</div>", unsafe_allow_html=True)
            st.audio(r['preview'])
            st.markdown(f"<a href='{r['url']}' target='_blank' class='download-link'>🔗 Freesound에서 다운로드</a>", unsafe_allow_html=True)