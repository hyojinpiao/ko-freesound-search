import streamlit as st
import requests
from urllib.parse import quote

# 인증 키
FREESOUND_API_KEY = "6xbTcaH4kDOXvKTCg8NJqZCTVKiRgGZI0C5S0hFX"
PAPAGO_CLIENT_ID = "ou64ob8r3r"
PAPAGO_CLIENT_SECRET = "nNqSptDXMb0e0hNp1JhJSiIFGN1qgWegWfS2DmDk"

def papago_translate(text):
    url = "https://openapi.naver.com/v1/papago/n2mt"
    headers = {
        "X-Naver-Client-Id": PAPAGO_CLIENT_ID,
        "X-Naver-Client-Secret": PAPAGO_CLIENT_SECRET
    }
    data = {
        "source": "ko",
        "target": "en",
        "text": text
    }
    try:
        res = requests.post(url, headers=headers, data=data, timeout=5)
        if res.status_code == 200:
            translated = res.json()['message']['result']['translatedText']
            st.write("📘 Papago 번역 결과:", translated)
            return translated
    except Exception as e:
        st.error(f"Papago 번역 오류: {e}")
    return text  # 실패 시 원문 그대로

def search_freesound(query):
    translated = papago_translate(query)
    encoded = quote(translated)
    url = f"https://freesound.org/apiv2/search/text/?query={encoded}&fields=name,id,previews&token={FREESOUND_API_KEY}&sort=downloads_desc&page_size=5"
    st.code(url, language='bash')  # 실제 요청 URL 출력
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            st.error(f"Freesound 응답 오류: {res.status_code}")
            return []
        data = res.json()
        st.write("🔢 Freesound 결과 수:", data.get("count", 0))
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
    except Exception as e:
        st.error(f"Freesound 요청 실패: {e}")
        return []

# UI
st.set_page_config(page_title="효과음 검색기", layout="centered")
st.title("🔍 효과음 검색기")
query = st.text_input("효과음을 검색하세요 (예: 비, 파도, 종소리)")

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
