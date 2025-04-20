import streamlit as st
import requests

API_KEY = "6xbTcaH4kDOXvKTCg8NJqZCTVKiRgGZI0C5S0hFX"

# 내 사이트에서 자동으로 불러오기
def search_my_soundmusic(query):
    url = f"https://freesoundcraft.com/wp-json/wp/v2/soundmusic?search={query}&per_page=5"
    res = requests.get(url)
    if res.status_code != 200:
        return []
    
    data = res.json()
    results = []
    for item in data:
        acf = item.get("acf", {})
        preview_url = acf.get("preview_link") or acf.get("preview_1")  # 대표 미리듣기
        if preview_url:
            results.append({
                "name": item["title"]["rendered"],
                "preview": preview_url,
                "url": item["link"]
            })
    return results

# Freesound API
def search_freesound(query):
    url = (
        f"https://freesound.org/apiv2/search/text/"
        f"?query={query}&fields=name,id,previews&token={API_KEY}"
        f"&sort=downloads_desc&page_size=5"
    )
    res = requests.get(url)
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

# 페이지 세팅
st.set_page_config(page_title="효과음 검색기", layout="centered")
st.markdown("### 🔍 효과음 검색기")
query = st.text_input("효과음을 검색하세요 (예: 비, rain, bell)")

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
