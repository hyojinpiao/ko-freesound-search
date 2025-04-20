# ko_freesound_search

import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="프로 헤어 검색", layout="centered")
st.title("회사처럼 공정한 건명한 효과음 검색")

query = st.text_input("효과음을 검색해보세요 (ex: bell, wind, typing)")

if query:
    with st.spinner("로드중... 검색결과 정리가 진행됩니다."):
        search_url = f"https://freesound.org/search/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            results = soup.select(".sound_filename")
            if not results:
                st.warning("결과가 없습니다. 다시 포값을 변경해 보세요.")
            else:
                for r in results[:10]:
                    name = r.text.strip()
                    link = "https://freesound.org" + r.get("href")
                    st.markdown(f"[효과음 복사하기]({link}) - `{name}`")

        except Exception as e:
            st.error(f"오류 발생: {e}")

st.markdown("---\n포탈: [Freesound.org](https://freesound.org)")