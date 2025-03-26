import streamlit as st
from navigation import assign_group


def init_session_state(api_pairs_grouped, stored_mapping, mapping_file):
    """세션 상태 변수를 초기화합니다."""
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "current_pair" not in st.session_state:
        st.session_state.current_pair = 0
    if "connections" not in st.session_state:
        st.session_state.connections = {}  # 그룹 내 API 쌍 별 연결 정보 저장
    if "show_warning" not in st.session_state:
        st.session_state.show_warning = False
    if "prolific_id_to_group" not in st.session_state:
        st.session_state.prolific_id_to_group = stored_mapping.copy()
    if "current_group" not in st.session_state:
        query_params = st.query_params
        if "PROLIFIC_PID" in query_params:
            st.session_state.prolific_id = query_params["PROLIFIC_PID"]
            st.session_state.current_group = assign_group(
                st.session_state.prolific_id, mapping_file, api_pairs_grouped
            )
        else:
            st.session_state.current_group = 0
