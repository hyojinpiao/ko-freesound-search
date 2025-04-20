import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
import json

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
    
    /* 검색 결과 디버그 정보 */
    .debug-info {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.8rem;
        white-space: pre-wrap;
        display: none;  /* 기본적으로 숨김 */
    }
</style>
""", unsafe_allow_html=True)

# 헤더 부분
st.markdown('<h1 class="main-header">🎵 프리사운드 효과음 검색기</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">고품질 무료 효과음을 검색하고 미리 들어보세요!</p>', unsafe_allow_html=True)

# API를 통해 직접 Freesound의 결과를 가져오는 함수
def search_freesound_direct(query, page=1, results_per_page=15, sort="score"):
    sounds = []
    
    try:
        # 1. API 요청 없이 직접 검색 결과 페이지를 스크래핑
        search_url = f"https://freesound.org/search/?q={quote_plus(query)}&page={page}&s={sort}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 디버깅을 위해 HTML 저장
        html_content = str(soup)[:5000]  # 처음 5000자만 디버깅용으로 저장
        
        # 검색 결과 아이템 찾기 (여러 가능한 CSS 선택자 시도)
        sound_items = soup.select(".bw-search__result") or soup.select(".sound_list_item") or soup.select(".sample_player_small")
        
        if not sound_items:
            # 직접 소스 코드에서 스크립트 데이터 추출 시도
            script_data = re.search(r'window\.pageData\s*=\s*({.*?});', response.text, re.DOTALL)
            if script_data:
                try:
                    data = json.loads(script_data.group(1))
                    if 'sounds' in data and isinstance(data['sounds'], list):
                        # API 응답에서 소리 정보 추출
                        for sound in data['sounds'][:results_per_page]:
                            sounds.append({
                                'id': sound.get('id', ''),
                                'name': sound.get('name', 'Unnamed Sound'),
                                'description': sound.get('description', '')[:150],
                                'username': sound.get('username', 'Unknown user'),
                                'license': sound.get('license', ''),
                                'preview': sound.get('previews', {}).get('preview-hq-mp3', ''),
                                'url': f"https://freesound.org/s/{sound.get('id', '')}/",
                                'tags': sound.get('tags', [])[:5],
                                'duration': sound.get('duration', 0),
                                'created': sound.get('created', ''),
                                'is_explicit': sound.get('is_explicit', False)
                            })
                except json.JSONDecodeError:
                    pass
        
        # HTML 파싱 방식으로 소리 정보 추출
        if not sounds:
            for idx, item in enumerate(sound_items[:results_per_page]):
                # 여러 선택자 시도
                sound_info = {}
                
                # 제목과 링크
                name_elem = (
                    item.select_one(".sound_filename") or 
                    item.select_one(".title a") or 
                    item.select_one("h3 a") or
                    item.select_one("a.title")
                )
                
                if name_elem:
                    sound_info['name'] = name_elem.text.strip()
                    link = name_elem.get("href", "")
                    sound_info['url'] = "https://freesound.org" + link if not link.startswith("http") else link
                    
                    # ID 추출
                    sound_id_match = re.search(r'/sounds/(\d+)/', link)
                    if sound_id_match:
                        sound_info['id'] = sound_id_match.group(1)
                    else:
                        sound_info['id'] = str(idx)
                
                # 설명 추출
                desc_elem = (
                    item.select_one(".description") or 
                    item.select_one(".metadata") or
                    item.select_one(".text")
                )
                sound_info['description'] = desc_elem.text.strip()[:150] if desc_elem else ""
                
                # 작성자 추출
                author_elem = (
                    item.select_one(".user a") or 
                    item.select_one(".username a") or
                    item.select_one(".user")
                )
                sound_info['username'] = author_elem.text.strip() if author_elem else "Unknown user"
                
                # 태그 추출
                tags = []
                tag_elems = item.select(".tag") or item.select(".tags a")
                for tag in tag_elems[:5]:
                    tags.append(tag.text.strip())
                sound_info['tags'] = tags
                
                # 미리듣기 URL 추출
                preview_elem = item.select_one("audio source") or item.select_one("[data-preview-url]")
                if preview_elem:
                    if preview_elem.has_attr('src'):
                        sound_info['preview'] = preview_elem['src']
                    elif preview_elem.has_attr('data-preview-url'):
                        sound_info['preview'] = preview_elem['data-preview-url']
                        
                # 대체 방법: ID 기반으로 URL 생성
                if 'preview' not in sound_info and 'id' in sound_info:
                    sound_id = sound_info['id']
                    prefix = sound_id[:3] if len(sound_id) >= 3 else sound_id
                    sound_info['preview'] = f"https://freesound.org/data/previews/{prefix}/{sound_id}/previews-hq-{sound_id}-HQ.mp3"
                
                sounds.append(sound_info)
        
        # 백업 방법: 최소한 이름과 ID만이라도 추출
        if not sounds:
            all_links = soup.select("a")
            sound_links = [a for a in all_links if '/sounds/' in a.get('href', '')]
            
            for idx, link in enumerate(sound_links[:results_per_page]):
                href = link.get('href', '')
                sound_id_match = re.search(r'/sounds/(\d+)/', href)
                
                if sound_id_match:
                    sound_id = sound_id_match.group(1)
                    prefix = sound_id[:3] if len(sound_id) >= 3 else sound_id
                    
                    sounds.append({
                        'id': sound_id,
                        'name': link.text.strip() or f"Sound {sound_id}",
                        'description': "",
                        'username': "Unknown user",
                        'preview': f"https://freesound.org/data/previews/{prefix}/{sound_id}/previews-hq-{sound_id}-HQ.mp3",
                        'url': f"https://freesound.org/s/{sound_id}/",
                        'tags': []
                    })
        
        return {
            'results': sounds,
            'total': len(sound_items),
            'debug': {
                'html_sample': html_content,
                'selectors_tried': [".bw-search__result", ".sound_list_item", ".sample_player_small"],
                'items_found': len(sound_items)
            }
        }
        
    except Exception as e:
        return {
            'results': [],
            'total': 0,
            'error': str(e),
            'debug': {
                'exception': str(e)
            }
        }

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
        result_count = st.selectbox("표시할 결과 수", [10, 15, 20, 30], index=0)
    with col2:
        sort_option = st.selectbox(
            "정렬 방식",
            ["관련성", "최신순", "다운로드순"],
            index=0
        )
    with col3:
        page_number = st.number_input("페이지", min_value=1, value=1, step=1)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 디버그 모드 토글 (개발용, 필요하면 활성화)
debug_mode = False

# 검색 처리
if query and (search_button or st.session_state.get('last_query') == query):
    # 현재 검색어 저장
    st.session_state['last_query'] = query
    
    with st.spinner("🔍 효과음을 찾고 있습니다..."):
        # 정렬 옵션 설정
        sort_map = {
            "관련성": "score",
            "최신순": "created desc",
            "다운로드순": "downloads desc"
        }
        sort_param = sort_map[sort_option]
        
        # 수정된 함수를 사용하여 검색
        search_results = search_freesound_direct(
            query=query, 
            page=page_number, 
            results_per_page=result_count,
            sort=sort_param
        )
        
        # 디버깅 정보 표시 (개발 중에만 사용)
        if debug_mode and 'debug' in search_results:
            st.markdown("<details><summary>디버그 정보</summary>", unsafe_allow_html=True)
            st.json(search_results['debug'])
            st.markdown("</details>", unsafe_allow_html=True)
        
        sounds = search_results.get('results', [])
        total_count = search_results.get('total', 0)
        
        if not sounds:
            st.markdown('''
            <div class="no-results">
                <h2>😕 검색 결과가 없습니다</h2>
                <p>다른 검색어를 시도하거나 영어로 검색해보세요!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            if 'error' in search_results:
                st.error(f"오류가 발생했습니다: {search_results['error']}")
        else:
            # 결과 카운트 표시
            st.markdown(f"### '{query}'에 대한 검색 결과 ({total_count}개 중 {len(sounds)}개 표시)")
            
            # 결과 카드 표시
            for sound in sounds:
                name = sound.get('name', 'Unnamed Sound')
                description = sound.get('description', '')
                username = sound.get('username', 'Unknown user')
                preview_url = sound.get('preview', '')
                sound_url = sound.get('url', '#')
                tags = sound.get('tags', [])
                
                # 결과 카드 HTML 생성
                st.markdown(f'''
                <div class="sound-card">
                    <div class="sound-title">{name}</div>
                    <div class="sound-info">작성자: {username}</div>
                    <p>{description}</p>
                    
                    <div class="tag-container">
                        {" ".join([f'<span class="tag">{tag}</span>' for tag in tags])}
                    </div>
                    
                    <audio controls>
                        <source src="{preview_url}" type="audio/mpeg">
                        브라우저가 오디오 재생을 지원하지 않습니다.
                    </audio>
                    
                    <div class="button-container">
                        <a href="{sound_url}" target="_blank" class="button-primary">상세정보</a>
                        <a href="{preview_url}" download class="button-secondary">미리듣기 다운로드</a>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
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
                if len(sounds) >= result_count:  # 다음 페이지가 있다고 가정
                    if st.button("다음 ▶", key="next"):
                        st.session_state["page_number"] = page_number + 1
                        st.experimental_rerun()
            
            with cols[4]:
                if len(sounds) >= result_count:  # 다음 페이지가 있다고 가정
                    if st.button("마지막 ▶▶", key="last"):
                        # 실제 마지막 페이지를 알 수 없으므로 임의의 큰 값(10)으로 이동
                        st.session_state["page_number"] = page_number + 10
                        st.experimental_rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# 간단한 하단 푸터
st.markdown('''
<div class="footer">
    <p>🔊 <a href="https://freesound.org" target="_blank">Freesound.org</a>의 효과음을 검색합니다</p>
</div>
''', unsafe_allow_html=True)