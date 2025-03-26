import json
import streamlit as st


def save_connections():
    """현재 API 쌍의 체크박스 상태를 세션 상태에 저장합니다."""
    st.session_state.connections[st.session_state.current_pair] = st.session_state.temp_connections


def next_page(api_pairs_grouped):
    """현재 그룹 내에서 다음 API 쌍으로 이동합니다."""
    save_connections()
    group_pairs = api_pairs_grouped[st.session_state.current_group]
    if st.session_state.current_pair + 1 < len(group_pairs):
        st.session_state.current_pair += 1
    st.session_state.temp_connections = st.session_state.connections.get(st.session_state.current_pair, [])


def previous_page():
    """현재 그룹 내에서 이전 API 쌍으로 이동합니다."""
    save_connections()
    if st.session_state.current_pair > 0:
        st.session_state.current_pair -= 1
    st.session_state.temp_connections = st.session_state.connections.get(st.session_state.current_pair, [])


def assign_group(prolific_id, mapping_file, api_pairs_grouped):
    """
    기존에 할당된 그룹이 있으면 반환하고, 없으면 새로운 그룹을 할당한 후 매핑 파일을 업데이트합니다.
    """
    if prolific_id in st.session_state.prolific_id_to_group:
        return st.session_state.prolific_id_to_group[prolific_id]
    assigned_group = len(st.session_state.prolific_id_to_group) % len(api_pairs_grouped)
    st.session_state.prolific_id_to_group[prolific_id] = assigned_group
    with open(mapping_file, "w") as f:
        json.dump(st.session_state.prolific_id_to_group, f, indent=4)
    return assigned_group
