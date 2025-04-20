import streamlit as st
import requests
from urllib.parse import quote

API_KEY = "6xbTcaH4kDOXvKTCg8NJqZCTVKiRgGZI0C5S0hFX"

# 🔤 간단 번역 맵
keyword_map = {
    "비": "rain",
    "물": "water",
    "종": "bell",
    "바람": "wind",
    "불": "fire",
    "새": "bird",
    "발자국": "footsteps",
    "기차": "train",
    "자동차": "car",
    "피아노": "piano",
    "고양이": "cat",
    "개": "dog",
}

def translate_keyword(kor_word):
    return keyword_map.get(kor_word.strip(), kor_word)

# ✅ 내 효과음
def search_my_soundmusic(query):
    url = f"https://freesoundcraft.com/wp-json/wp/v2/soundmusic?search={quote(query)}&per_page=5"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    data = res.json()
    results = []
    for item in data:
        acf = item.get("acf", {})
        preview_url = None
        if isinstance(acf, list):
            for entry in acf:
                if isinstance(entry, dict):
                    preview_url = entry.get("preview_link") or entry.get("preview_1")
                    if preview_url:
                        break
        elif isinstance(acf, dict):
            preview_url = acf.get("preview_link") or acf.get("preview_1")
        if preview_url:
            results.append({
                "name": item["title"]["rendered"],
                "preview": preview_url,
                "url": item["link"]
            })
    return results

# ✅ Freesound (영어로 번역 후 검색)
def search_freesound(query):
    translated = translate_keyword(query)
    encoded = quote(translated)
    url = f"https://freesound.org/apiv2/search/text/?query={encoded}&fields=name,id,previews&token={API_KEY}&sort=downloads_desc&page_size=5"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"Freesound API 오류 (코드 {res.status_code})")
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

# ✅ UI
st.set_page_config(page_title="효과음 검색기", layout="centered")
st.markdown("### 🔍 효과음 검색기")
query = st.text_input("효과음을 검색하세요 (예: 비, 불, rain, bell 등)")

if st.button("검색") and query:
    with st.spinner("검색 중..."):
        my_results = search_my_soundmusic(query)
        fs_results = search_freesound(query)

        if my_results:
            st.markdown("### 🎧 내가 만든 효과음")
            for r in my_results:
                st.markdown(f"**🎵 {r['name']}**")
                st.audio(r['preview'])
                st.markdown(f"[내 사이트에서 보기]({r['url']})", unsafe_allow_html=True)

        if fs_results:
            st.markdown("### 🌍 Freesound 효과음")
            for r in fs_results:
                st.markdown(f"**🎵 {r['name']}**")
                st.audio(r['preview'])
                st.markdown(f"[Freesound에서 보기]({r['url']})", unsafe_allow_html=True)

        if not my_results and not fs_results:
            st.warning("검색 결과가 없습니다.")
