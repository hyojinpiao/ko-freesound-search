import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

# 페이지 설정
st.set_page_config(
    page_title="프리사운드 효과음 검색기",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .search-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .sound-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .sound-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .sound-title {
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 5px;
    }
    
    .sound-info {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    
    .button-primary {
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.9rem;
        margin-right: 10px;
        cursor: pointer;
    }
    
    .button-secondary {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.9rem;
        cursor: pointer;
    }
    
    .pagination {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    
    .no-results {
        text-align: center;
        padding: 40px;
        background-color: #f9f9f9;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    /* 반응형 디자인을 위한 미디어 쿼리 */
    @media (max-width: 768px) {
        .sound-card {
            padding: 10px;
        }
        .sound-title {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 헤더 부분
st.markdown('<h1 class="main-header">🎵 프리사운드 효과음 검색기</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">고품질 무료 효과음을 검색하고 미리 들어보세요!</p>', unsafe_allow_html=True)

# 사이드바 필터 옵션
with st.sidebar:
    st.header("검색 필터")
    
    sort_option = st.selectbox(
        "정렬 방식",
        ["관련성", "최신순", "다운로드순", "평점순"],
        index=0
    )
    
    duration = st.slider(
        "재생 시간(초)",
        0, 300, (0, 300)
    )
    
    license_type = st.multiselect(
        "라이센스 유형",
        ["Attribution", "Attribution Noncommercial", "Creative Commons 0"],
        default=[]
    )
    
    file_type = st.multiselect(
        "파일 형식",
        ["WAV", "MP3", "FLAC", "OGG", "AIFF"],
        default=[]
    )
    
    st.markdown("---")
    st.markdown("### 🔍 검색 팁")
    st.markdown("- 영어 키워드로 검색하면 더 많은 결과를 찾을 수 있습니다")
    st.markdown("- 구체적인 키워드를 사용해보세요 (예: 'wind'보다는 'gentle wind')")
    st.markdown("- 태그를 활용하세요 (예: 'tag:nature')")

# 메인 콘텐츠
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        query = st.text_input("효과음을 검색해보세요", placeholder="예: bell, rain, footsteps, keyboard 등")
        cols = st.columns([1, 1])
        with cols[0]:
            result_count = st.selectbox("표시할 결과 수", [10, 20, 30, 50], index=0)
        with cols[1]:
            page_number = st.number_input("페이지", min_value=1, value=1, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

if query:
    with st.spinner("🔍 효과음을 찾고 있습니다..."):
        # 검색어 URL 인코딩
        encoded_query = quote_plus(query)
        
        # 정렬 옵션 설정
        sort_map = {
            "관련성": "score",
            "최신순": "created desc",
            "다운로드순": "downloads desc",
            "평점순": "rating desc"
        }
        sort_param = sort_map[sort_option]
        
        # 페이지네이션 처리
        page_param = page_number
        
        # 검색 URL 구성
        search_url = f"https://freesound.org/search/?q={encoded_query}&page={page_param}&sort={sort_param}"
        
        # 필터 추가
        if duration != (0, 300):
            search_url += f"&f=duration:[{duration[0]} TO {duration[1]}]"
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            # 웹사이트에서 검색 결과 요청
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 소리 아이템 컨테이너 찾기
            sound_items = soup.select(".bw-search__result")
            
            if not sound_items:
                st.markdown('''
                <div class="no-results">
                    <h2>😕 검색 결과가 없습니다</h2>
                    <p>다른 검색어를 시도하거나 영어로 검색해보세요!</p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                # 결과 카운트 표시
                st.markdown(f"### '{query}'에 대한 검색 결과 ({len(sound_items)}개 중 {min(result_count, len(sound_items))}개 표시)")
                
                # 최대 result_count개의 결과 출력
                for item in sound_items[:result_count]:
                    try:
                        # 효과음 이름과 링크 추출
                        name_elem = item.select_one(".bw-search__result_header h3 a")
                        if not name_elem:
                            continue
                            
                        name = name_elem.text.strip()
                        link = "https://freesound.org" + name_elem.get("href")
                        sound_id = re.search(r'/sounds/(\d+)/', link)
                        sound_id = sound_id.group(1) if sound_id else None
                        
                        # 효과음 설명 추출
                        description_elem = item.select_one(".bw-search__result_tags")
                        description = description_elem.text.strip() if description_elem else "설명 없음"
                        
                        # 작성자와 날짜 추출
                        author_elem = item.select_one(".bw-search__result_user a")
                        author = author_elem.text.strip() if author_elem else "알 수 없음"
                        
                        # 재생시간, 다운로드 수 등 정보 추출
                        meta_elem = item.select_one(".bw-search__result_collection")
                        meta_info = meta_elem.text.strip() if meta_elem else ""
                        
                        # 미리듣기 URL 생성
                        preview_url = f"https://freesound.org/data/previews/{sound_id[:3] if sound_id else '000'}/{sound_id}/previews-hq-{sound_id}-HQ.mp3" if sound_id else ""
                        
                        # 결과 카드 표시
                        st.markdown(f'''
                        <div class="sound-card">
                            <div class="sound-title">{name}</div>
                            <div class="sound-info">올린이: {author} | {meta_info}</div>
                            <p>{description}</p>
                            <audio controls style="width:100%; margin:10px 0;">
                                <source src="{preview_url}" type="audio/mpeg">
                                브라우저가 오디오 재생을 지원하지 않습니다.
                            </audio>
                            <div>
                                <a href="{link}" target="_blank" class="button-primary">상세 정보</a>
                                <a href="{preview_url}" download class="button-secondary">미리듣기 다운로드</a>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"결과 파싱 중 오류 발생: {e}")
                
                # 페이지네이션 버튼
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown('<div class="pagination">', unsafe_allow_html=True)
                    if page_number > 1:
                        prev_page = page_number - 1
                        st.button(f"◀ 이전 페이지", 
                                key=f"prev_{prev_page}", 
                                on_click=lambda: st.session_state.update({"page_number": prev_page}))
                    
                    st.write(f"페이지 {page_number}")
                    
                    next_page = page_number + 1
                    st.button(f"다음 페이지 ▶", 
                            key=f"next_{next_page}", 
                            on_click=lambda: st.session_state.update({"page_number": next_page}))
                    st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.write("네트워크 오류가 발생했거나 사이트에 접근할 수 없습니다. 나중에 다시 시도해주세요.")

# 하단 푸터
st.markdown('''
<div class="footer">
    <p>🔊 <a href="https://freesound.org" target="_blank">Freesound.org</a>에서 제공하는 무료 효과음 검색 서비스입니다.</p>
    <p>이 사이트는 Freesound.org와 제휴 관계가 없으며, 모든 효과음은 원 사이트의 라이센스를 따릅니다.</p>
    <p>라이센스를 확인하고 사용해 주세요.</p>
</div>
''', unsafe_allow_html=True)