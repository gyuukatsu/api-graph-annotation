import streamlit as st
from file_loader import load_mapping, prepare_annotation_pairs
from session_state import init_session_state
from pages import render_main_page, render_annotation_page, render_finish_page

# Streamlit 페이지 설정
st.set_page_config(layout="wide", page_title="API Parameter Compatibility Matching")

# 파일 경로
API_PAIRS_FILE = "./preprocessed_data/nestful_api_pairs_for_annotation_v3.json"
MAPPING_FILE = "./preprocessed_data/prolific_id_mapping.json"

# 데이터 로딩
api_pairs_grouped = prepare_annotation_pairs(API_PAIRS_FILE, pairs_per_group=47)
stored_mapping = load_mapping(MAPPING_FILE)

# 세션 상태 초기화
init_session_state(api_pairs_grouped, stored_mapping, MAPPING_FILE)

# 세션 상태에 따라 페이지 렌더링
if st.session_state.page == "main":
    render_main_page()
elif st.session_state.page == "annotation":
    render_annotation_page(api_pairs_grouped)
elif st.session_state.page == "finish":
    render_finish_page()
