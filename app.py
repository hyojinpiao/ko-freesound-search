import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

# 페이지 설정
st.set_page_config(
    page_title="프리사운드 효과음 검색기",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 추가
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .search-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .search-button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 5px;
        padding: 5px 15px;
        font-size: 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .search-button:hover {
        background-color: #2563EB;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .sound-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        border-left: 4px solid #2563EB;
    }
    
    .sound-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .sound-title {
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 5px;
        color: #1E3A8A;
    }
    
    .sound-info {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 8px 0;
    }
    
    .tag {
        background-color: #E5E7EB;
        color: #4B5563;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    .button-primary {
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.9rem;
        margin-right: 10px;
        cursor: pointer;
        display: inline-block;
    }
    
    .button-secondary {
        background-color: #10B981;
        color: white;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.9rem;
        cursor: pointer;
        display: inline-block;
    }
    
    .pagination {
        display: flex;
        gap: 10px;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    
    .pagination-button {
        background-color: #E5E7EB;
        color: #4B5563;
        border: none;
        padding: 5px 15px;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    
    .pagination-button-active {
        background-color: #2563EB;
        color: white;
    }
    
    .footer {
        text-align: center;
        margin-top: 20px;
        padding: 15px;
        background-color: #f0f2f6;
        border-radius: 10px;
        font-size: 0.9rem;
        color: #666;
    }
    
    .no-results {
        text-align: center;
        padding: 30px;
        background-color: #f9f9f9;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    audio {
        width: 100%;
        margin: 10px 0;
    }
    
    .button-container {
        margin-top: 10px;
        display: flex;
        gap: 10px;
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

# 검색 컨테이너
with st.container():
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    # 검색 입력 필드와 버튼을 같은 줄에 배치
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("", placeholder="효과음을 검색해보세요 (예: bell, rain, footsteps 등)", label_visibility="collapsed")
    with col2:
        search_button = st.button("검색하기", use_container_width=True)
    
    # 필터 옵션들을 한 줄에 배치
    col1, col2, col3 = st.columns(3)
    with col1:
        result_count = st.selectbox("표시할 결과 수", [10, 20, 30, 50], index=0)
    with col2:
        sort_option = st.selectbox(
            "정렬 방식",
            ["관련성", "최신순", "다운로드순"],
            index=0
        )
    with col3:
        page_number = st.number_input("페이지", min_value=1, value=1, step=1)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 검색 처리
if query and (search_button or st.session_state.get('last_query') == query):
    # 현재 검색어 저장
    st.session_state['last_query'] = query
    
    with st.spinner("🔍 효과음을 찾고 있습니다..."):
        # 검색어 URL 인코딩
        encoded_query = quote_plus(query)
        
        # 정렬 옵션 설정
        sort_map = {
            "관련성": "score",
            "최신순": "created desc",
            "다운로드순": "downloads desc"
        }
        sort_param = sort_map[sort_option]
        
        # 검색 URL 구성
        search_url = f"https://freesound.org/search/?q={encoded_query}&page={page_number}&sort={sort_param}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            # 웹사이트에서 검색 결과 요청
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 소리 아이템들 찾기 - 여러 선택자 시도
            sound_items = soup.select(".bw-search__result") or soup.select(".sound_list_entity") or soup.select(".sample_player_small")
            
            # 결과 카운트를 얻기 위한 시도
            count_text = soup.select_one(".bw-search__num-results")
            total_count = "여러" if not count_text else count_text.text.strip()
            
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
                for idx, item in enumerate(sound_items[:result_count]):
                    try:
                        # 여러 선택자를 시도하며 데이터 추출
                        
                        # 1. 첫 번째 방법: 새 디자인
                        name_elem = item.select_one(".bw-search__result_header h3 a") or item.select_one("h3 a")
                        
                        # 2. 두 번째 방법: 이전 디자인
                        if not name_elem:
                            name_elem = item.select_one(".title a")
                        
                        # 데이터 없으면 건너뛰기
                        if not name_elem:
                            continue
                            
                        name = name_elem.text.strip()
                        link = "https://freesound.org" + name_elem.get("href") if not name_elem.get("href").startswith("http") else name_elem.get("href")
                        
                        # ID 추출 시도
                        sound_id = re.search(r'/sounds/(\d+)/', link)
                        if not sound_id:
                            sound_id = re.search(r'id=(\d+)', link)
                        sound_id = sound_id.group(1) if sound_id else str(idx)
                        
                        # 설명 추출 시도
                        description_elem = (
                            item.select_one(".bw-search__result_tags") or 
                            item.select_one(".description") or 
                            item.select_one(".metadata")
                        )
                        description = description_elem.text.strip() if description_elem else "설명 없음"
                        
                        # 태그 추출 시도
                        tags = []
                        tag_elems = item.select(".tag") or item.select(".tags a")
                        for tag in tag_elems[:5]:  # 최대 5개 태그만
                            tags.append(tag.text.strip())
                        
                        # 작성자 추출 시도
                        author_elem = (
                            item.select_one(".bw-search__result_user a") or 
                            item.select_one(".user a") or 
                            item.select_one(".user")
                        )
                        author = author_elem.text.strip() if author_elem else "알 수 없음"
                        
                        # 미리듣기 URL 생성 시도
                        # 1. data-waveform에서 추출
                        preview_url = ""
                        waveform_div = item.select_one("[data-waveform]")
                        if waveform_div:
                            preview_data = waveform_div.get("data-waveform", "")
                            preview_match = re.search(r'"preview_url":"([^"]+)"', preview_data)
                            if preview_match:
                                preview_url = preview_match.group(1).replace("\\/", "/")
                        
                        # 2. 대체 방법: ID 기반으로 URL 생성
                        if not preview_url:
                            preview_url = f"https://freesound.org/data/previews/{sound_id[:3] if len(sound_id) >= 3 else sound_id}/{sound_id}/previews-hq-{sound_id}-HQ.mp3"
                        
                        # 결과 카드 표시
                        st.markdown(f'''
                        <div class="sound-card">
                            <div class="sound-title">{name}</div>
                            <div class="sound-info">작성자: {author}</div>
                            <p>{description[:150]}{"..." if len(description) > 150 else ""}</p>
                            
                            <div class="tag-container">
                                {" ".join([f'<span class="tag">{tag}</span>' for tag in tags])}
                            </div>
                            
                            <audio controls>
                                <source src="{preview_url}" type="audio/mpeg">
                                브라우저가 오디오 재생을 지원하지 않습니다.
                            </audio>
                            
                            <div class="button-container">
                                <a href="{link}" target="_blank" class="button-primary">상세정보</a>
                                <a href="{preview_url}" download class="button-secondary">미리듣기 다운로드</a>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"결과 {idx+1} 파싱 중 오류 발생")
                
                # 페이지네이션 버튼
                st.markdown('<div class="pagination">', unsafe_allow_html=True)
                cols = st.columns([1, 1, 3, 1, 1])
                
                with cols[0]:
                    if page_number > 1:
                        if st.button("◀◀ 처음", key="first"):
                            st.session_state["page_number"] = 1
                            st.experimental_rerun()
                
                with cols[1]:
                    if page_number > 1:
                        if st.button("◀ 이전", key="prev"):
                            st.session_state["page_number"] = page_number - 1
                            st.experimental_rerun()
                
                with cols[2]:
                    st.markdown(f"<div style='text-align:center; font-weight:bold;'>페이지 {page_number}</div>", unsafe_allow_html=True)
                
                with cols[3]:
                    if len(sound_items) >= result_count:  # 다음 페이지가 있다고 가정
                        if st.button("다음 ▶", key="next"):
                            st.session_state["page_number"] = page_number + 1
                            st.experimental_rerun()
                
                with cols[4]:
                    if len(sound_items) >= result_count:  # 다음 페이지가 있다고 가정
                        if st.button("마지막 ▶▶", key="last"):
                            # 실제 마지막 페이지를 알 수 없으므로 임의의 큰 값(10)으로 이동
                            st.session_state["page_number"] = page_number + 10
                            st.experimental_rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            st.write("네트워크 오류가 발생했거나 사이트에 접근할 수 없습니다. 나중에 다시 시도해주세요.")

# 간단한 하단 푸터
st.markdown('''
<div class="footer">
    <p>🔊 <a href="https://freesound.org" target="_blank">Freesound.org</a>의 효과음을 검색합니다</p>
</div>
''', unsafe_allow_html=True)