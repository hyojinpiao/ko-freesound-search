import streamlit as st
import requests
from urllib.parse import quote

# Freesound API 인증 키
FREESOUND_API_KEY = "6xbTcaH4kDOXvKTCg8NJqZCTVKiRgGZI0C5S0hFX"

# Freesound 검색 함수
def search_freesound(query):
    encoded = quote(query)
    url = f"https://freesound.org/apiv2/search/text/?query={encoded}&fields=name,id,previews&token={FREESOUND_API_KEY}&sort=downloads_desc&page_size=5"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return []
        data = res.json()
        results = []
        for s in data.get("results", []):
            preview = s.get("previews", {}).get("preview-hq-mp3")
            if preview:
                results.append({
                    "name": s.get("name", "Unnamed"),
                    "preview": preview,
                    "url": f"https://freesound.org/s/{s['id']}/"
                })
        return results
    except:
        return []

# UI 구성
st.set_page_config(page_title="효과음 검색기", layout="centered")

st.markdown("<h4 style='text-align: center;'>🔍 효과음 검색기</h4>", unsafe_allow_html=True)
query = st.text_input("효과음을 검색하세요 (예: 비, 파도, 종소리)", "")

if st.button("검색") and query:
    with st.spinner("🔎 검색 중..."):
        results = search_freesound(query)

        if results:
            for r in results:
                st.markdown(f"**🎵 {r['name']}**")
                st.audio(r['preview'])
                st.markdown(f"[Freesound에서 보기]({r['url']})", unsafe_allow_html=True)
        else:
            st.warning("검색 결과가 없습니다.")
            st.markdown("🔎 찾고있는 효과음이 없다면 아래에서 Freesound를 검색해보세요.", unsafe_allow_html=True)
