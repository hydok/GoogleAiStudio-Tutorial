import os
import streamlit as st
from downloader import download_audio, get_video_info
from transcriber import transcribe_youtube_audio
from history_manager import (
    load_history,
    add_history_item,
    delete_history_item,
    clear_all_history,
)

# 페이지 기본 설정
st.set_page_config(
    page_title="YouTube Audio Transcriber & History",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 상단 가림 방지 및 여백 최적화 커스텀 스타일
st.markdown(
    """
    <style>
    /* Streamlit 기본 헤더(3.5rem 높이)와 겹치지 않도록 상단 여백을 충분히 확보 */
    .block-container {
        padding-top: 4.8rem !important;
        padding-bottom: 3.5rem !important;
    }
    /* Streamlit 기본 헤더 투명화로 클릭 방해 제거 */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    .brand-title {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #1e1e1e;
        margin: 0;
        padding: 0;
    }
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #6c757d;
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
    }
    /* 상단 메뉴 라디오 버튼 바 스타일링 */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 8px;
        background: #f1f3f5;
        padding: 6px 10px;
        border-radius: 20px;
        width: fit-content;
        margin-left: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 🌟 상단 고정형 헤더 및 네비게이션 바 (가림 현상 완벽 방지)
# ==============================================================================
with st.container():
    nav_col1, nav_col2 = st.columns([1, 1], vertical_alignment="center")

    with nav_col1:
        st.markdown('<div class="brand-title">🎙️ YouTube Transcriber AI</div>', unsafe_allow_html=True)

    with nav_col2:
        menu_options = ["🎙️ 새 영상 변환", "📜 변환 기록 (History)"]
        
        # st.segmented_control 지원 시 우선 사용, 미지원 시 horizontal radio 사용
        if hasattr(st, "segmented_control"):
            selected_menu = st.segmented_control(
                "메뉴 이동",
                options=menu_options,
                default=menu_options[0],
                label_visibility="collapsed",
            )
            menu = selected_menu or menu_options[0]
        else:
            menu = st.radio(
                "메뉴 이동",
                options=menu_options,
                horizontal=True,
                label_visibility="collapsed",
            )

# 상단 바와 본문 사이의 시원한 간격
st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# ==============================================================================
# 사이드바 설정 (API 키 설정 및 부가 안내)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ API 설정")
    
    env_api_key = os.environ.get("GEMINI_API_KEY", "")
    api_key = st.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        help="Google AI Studio(aistudio.google.com)에서 발급받은 API 키를 입력하세요.",
    )

    if not api_key:
        st.warning("⚠️ API 키가 필요합니다. 상단에 입력하거나 터미널에서 환경변수를 설정해 주세요.")

    st.markdown("---")
    st.markdown(
        """
        ### 📌 주요 기술 스택
        * **오디오 추출**: `yt-dlp` 무손실 스트림 다운로드
        * **AI 분석 엔진**: `gemini-3.6-flash` 멀티모달 오디오
        * **로컬 데이터베이스**: JSON 기반 히스토리 영구 저장
        """
    )
    st.caption("Google AI Studio Tutorial • 2026")


# ==============================================================================
# 1. 🎙️ 새 영상 변환 페이지 (View)
# ==============================================================================
if menu == "🎙️ 새 영상 변환":
    st.markdown('<div class="main-title">유튜브 오디오 추출 & AI 트랜스크립터</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">유튜브 영상 URL을 입력하면 고음질 오디오를 다운로드하고, Gemini AI가 전문 전사 및 핵심 요약을 생성합니다.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([5, 1])
    with col1:
        youtube_url = st.text_input(
            "유튜브 영상 주소 (URL)",
            placeholder="https://www.youtube.com/watch?v=... 또는 https://youtu.be/...",
            label_visibility="collapsed",
        )
    with col2:
        start_button = st.button("🚀 변환 시작", type="primary", use_container_width=True)

    if start_button:
        if not youtube_url.strip():
            st.error("❌ 유튜브 영상 URL을 입력해 주세요.")
        elif not api_key.strip():
            st.error("❌ 좌측 사이드바(또는 환경변수)에 Google Gemini API Key를 설정해 주세요.")
        else:
            try:
                with st.status("🔍 유튜브 영상 정보를 분석하는 중...", expanded=True) as status:
                    st.write("1️⃣ 영상 메타데이터 불러오는 중...")
                    info = get_video_info(youtube_url)
                    
                    col_thumb, col_meta = st.columns([1, 2])
                    with col_thumb:
                        if info.get("thumbnail"):
                            st.image(info["thumbnail"], use_container_width=True)
                    with col_meta:
                        st.markdown(f"### {info['title']}")
                        st.markdown(f"**채널**: {info['uploader']} | **재생시간**: {info['duration_str']}")
                    
                    st.write("2️⃣ 고음질 오디오 스트림 다운로드 중...")
                    audio_path, _ = download_audio(youtube_url, output_dir="downloads")
                    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
                    st.write(f"✅ 오디오 다운로드 완료! (크기: {file_size_mb:.1f} MB)")
                    
                    st.audio(audio_path)

                    st.write("3️⃣ Gemini 3.6 Flash 모델로 AI 전사 및 요약 분석 중...")
                    transcript_result = transcribe_youtube_audio(audio_path, api_key=api_key)
                    
                    # 히스토리에 자동 누적
                    add_history_item(info, audio_path, transcript_result)

                    status.update(label="🎉 모든 처리가 성공적으로 완료되었습니다!", state="complete", expanded=False)

                st.success("✨ 트랜스크립트 생성이 완료되었습니다! 상단의 [📜 변환 기록 (History)] 메뉴에서도 언제든 다시 확인할 수 있습니다.")

                tab1, tab2 = st.tabs(["📑 전체 리포트 (요약 + 전문)", "🎧 오디오 재생"])

                with tab1:
                    safe_title = info['title'].replace(" ", "_")[:30]
                    st.download_button(
                        label="💾 전사 결과 텍스트(.txt) 다운로드",
                        data=transcript_result,
                        file_name=f"{safe_title}_transcript.txt",
                        mime="text/plain",
                        type="primary",
                    )
                    st.markdown(transcript_result)

                with tab2:
                    st.markdown("#### 🎵 추출된 원본 오디오")
                    st.audio(audio_path)
                    st.caption(f"로컬 파일 위치: `{audio_path}`")

            except Exception as e:
                st.error(f"⚠️ 오류가 발생했습니다: {e}")


# ==============================================================================
# 2. 📜 변환 기록 (History) 페이지 (View)
# ==============================================================================
elif menu == "📜 변환 기록 (History)":
    st.markdown('<div class="main-title">변환 히스토리 (History)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">지금까지 변환했던 모든 유튜브 영상들의 AI 트랜스크립트와 오디오를 다시 열람하고 다운로드할 수 있습니다.</div>',
        unsafe_allow_html=True,
    )

    history = load_history()

    if not history:
        st.info("💡 아직 변환한 히스토리 기록이 없습니다. 상단의 '🎙️ 새 영상 변환' 메뉴에서 영상을 변환해 보세요!")
    else:
        # 상단 통계 메트릭 & 검색창 & 전체 삭제
        col_metric, col_search, col_clear = st.columns([1, 2, 1], vertical_alignment="bottom")
        with col_metric:
            st.metric("총 변환된 영상", f"{len(history)} 개")
        with col_search:
            search_query = st.text_input("🔍 영상 제목 또는 채널명 검색", placeholder="검색어를 입력하세요...", label_visibility="visible")
        with col_clear:
            if st.button("🗑️ 전체 기록 삭제", type="secondary", use_container_width=True):
                clear_all_history()
                st.toast("모든 히스토리가 삭제되었습니다.")
                st.rerun()

        st.markdown("---")

        # 검색 쿼리 필터링
        filtered_history = history
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_history = [
                item for item in history
                if q in item.get("title", "").lower() or q in item.get("uploader", "").lower()
            ]

        if not filtered_history:
            st.warning("검색 결과와 일치하는 기록이 없습니다.")
        else:
            for idx, item in enumerate(filtered_history):
                with st.expander(f"🎬 [{item['created_at']}] {item['title']} ({item['duration_str']})", expanded=(idx == 0)):
                    col_left, col_right = st.columns([1, 2])
                    
                    with col_left:
                        if item.get("thumbnail"):
                            st.image(item["thumbnail"], use_container_width=True)
                        st.markdown(f"**채널**: {item.get('uploader', '알 수 없음')}")
                        st.markdown(f"**변환 일시**: {item.get('created_at', '-')}")
                        st.markdown(f"**재생 시간**: {item.get('duration_str', '-')}")
                        
                        if item.get("youtube_url"):
                            st.link_button("🔗 원본 유튜브 영상 보기", item["youtube_url"], use_container_width=True)

                        # 디스크에 저장된 오디오 재생
                        audio_file = item.get("audio_path", "")
                        if audio_file and os.path.exists(audio_file):
                            st.markdown("---")
                            st.markdown("🎵 **추출된 오디오 재생**")
                            st.audio(audio_file)
                        
                        st.markdown("---")
                        # 개별 항목 삭제
                        if st.button(f"🗑️ 이 기록 삭제", key=f"del_{item['id']}", use_container_width=True):
                            delete_history_item(item["id"])
                            st.toast("해당 항목이 삭제되었습니다.")
                            st.rerun()

                    with col_right:
                        safe_title = item['title'].replace(" ", "_")[:30]
                        st.download_button(
                            label="💾 트랜스크립트 텍스트(.txt) 다운로드",
                            data=item.get("transcript", ""),
                            file_name=f"{safe_title}_transcript.txt",
                            mime="text/plain",
                            key=f"dl_{item['id']}",
                        )
                        st.markdown(item.get("transcript", "내용 없음"))
