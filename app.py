import streamlit as st
import requests

API_KEY = "6xbTcaH4kDOXvKTCg8NJqZCTVKiRgGZI0C5S0hFX"

def search_freesound_api(query):
    url = f"https://freesound.org/apiv2/search/text/?query={query}&fields=name,id,previews&token={API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        st.error("API 요청 실패 😢")
        st.text(f"응답 코드: {res.status_code}")
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

st.set_page_config(page_title="🎧 효과음 검색기", layout="centered")
st.title("🔎 Freesound 효과음 검색기")
query = st.text_input("효과음을 검색하세요 (예: rain, bell)")

if st.button("검색") and query:
    with st.spinner("검색 중..."):
        results = search_freesound_api(query)
        if not results:
            st.warning("결과가 없습니다. 영어로 검색해보세요.")
        for r in results:
            st.markdown(f"### 🎵 {r['name']}")
            st.audio(r['preview'])
            st.markdown(f"[🔗 Freesound에서 다운로드]({r['url']})", unsafe_allow_html=True)
