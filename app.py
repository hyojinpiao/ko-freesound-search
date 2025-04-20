import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="효과음 검색기 | Freesound", layout="centered")
st.title("공정하고 깔끔한 효과음 검색기")

# 사용자 입력을 받는 필드
query = st.text_input("효과음을 검색해보세요 (ex: bell, wind, typing)")

if query:
    with st.spinner("검색 중..."):
        search_url = f"https://freesound.org/search/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            # Freesound 웹사이트에서 검색 결과를 요청
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # 결과에서 효과음 이름을 찾는 코드
            results = soup.select(".sound_filename")
            if not results:
                st.warning("검색 결과가 없습니다. 검색어를 다시 확인해 보세요.")
            else:
                # 최대 10개의 결과를 출력
                for r in results[:10]:
                    name = r.text.strip()  # 효과음 이름
                    link = "https://freesound.org" + r.get("href")  # 효과음 링크
                    st.markdown(f"[효과음 복사하기]({link}) - `{name}`")

        except Exception as e:
            st.error(f"오류 발생: {e}")

# 하단의 포탈 링크 추가
st.markdown("---\n포탈: [Freesound.org](https://freesound.org)")
