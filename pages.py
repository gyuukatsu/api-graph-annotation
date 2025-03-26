import streamlit as st
import pandas as pd
import json
from datetime import datetime
from navigation import next_page, previous_page, save_connections


def render_instructions():
    """태스크 설명을 반환합니다."""
    instructions = """
    ---
    **< Task Overview >**

    Your task is to establish connections between the output parameters of a source API and the input parameters of a target API, based on their meaning and compatibility. Full documentation for both APIs will be provided, including descriptions, input parameters, and output parameters.

    For each output parameter from the source API:
    - Select one or more input parameters from the target API if they are compatible, even if their names or data types differ, provided the underlying meaning aligns.
    - If no suitable input parameter exists, select "None of the above".

    ---
    **< Annotation Rules >**

    **1. Prioritize Parameter Descriptions**
    - Do not rely solely on parameter names to infer their meaning.
    - Always refer to the parameter description, as names can be misleading.
    - Example: **`username`** might actually refer to an email address. The description provides clarity.

    **2. Complete Information Matching**
    - A source parameter can be linked to multiple target parameters if it contains all necessary information.
    - Example: **`full_name`** (source) → **`first_name`**, **`last_name`** (target).
    - Partial matches are not allowed when a single source parameter doesn't contain all information needed by the target parameter.
    - Example: **`first_name`** (source) cannot be connected to **`full_name`** (target).

    **3. Type & Format Compatibility is Flexible**
    - Parameter types do not have to be identical as long as the value meaning is preserved.
    - Example: If **`height`** is a string in the source API but an integer in the target API, you can still connect them.
    - Format differences are also acceptable if the underlying data is the same.
    - Example: A date in "YYYY-MM-DD" format can be connected to a target parameter requiring "MM/DD/YYYY" format.

    ---
    **< Additional Notes >**
    - If a parameter has no corresponding match, select "None of the above" instead of making an inaccurate connection.
    - If multiple valid input parameters exist, select all applicable ones.
    - Ensure that the selected connections are logically correct and meaningful.
    ---
    """
    return instructions


def render_main_page():
    """태스크 개요와 시작 버튼을 표시하는 메인 페이지를 렌더링합니다."""
    _, middle, _ = st.columns([2, 5, 2])
    with middle:
        st.title("API Parameter Compatibility Matching")
        st.write(render_instructions())
        agree = st.checkbox("I have read and understood the task instructions.")
        if agree and st.button("Start Annotation"):
            st.session_state.page = "annotation"
            st.rerun()


def render_annotation_page(api_pairs_grouped: list):
    """어노테이션 작업 페이지를 렌더링합니다."""
    st.write("### API Parameter Compatibility Matching")
    st.write("Annotate connections between the source and target API parameters below.")

    with st.expander("**Task Instructions**"):
        st.write(render_instructions())

    st.divider()

    col1, col2 = st.columns(2, gap="small")
    group_pairs = api_pairs_grouped[st.session_state.current_group]
    pair = group_pairs[st.session_state.current_pair]
    source_api = pair[0]
    target_api = pair[1]

    # 이전에 저장된 연결 정보를 불러옵니다.
    st.session_state.temp_connections = st.session_state.connections.get(st.session_state.current_pair, [])

    # Source API 표시
    with col1:
        with st.container(height=700):
            st.write("#### Source API")
            st.write(
                f"**<span style='color: blue;'>{source_api.get('name', 'Error')}</span>** : {source_api.get('description', '')}",
                unsafe_allow_html=True,
            )
            st.write("\n")
            st.write("**[Input Parameters]**")
            source_input_params = source_api.get("input_params", [])
            if source_input_params:
                source_input_data = [
                    {
                        "Parameter Name": arg.get("name", "Error"),
                        "Type": arg.get("type", ""),
                        "Description": arg.get("description", ""),
                    }
                    for arg in source_input_params
                ]
                df_source_input = pd.DataFrame(source_input_data)
                st.markdown(
                    """
                    <style>
                        table td:nth-of-type(1) {width: 25% !important;}
                        table td:nth-of-type(2) {width: 11% !important;}
                        table td:nth-of-type(3) {width: 59% !important;}
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                st.table(df_source_input)

            st.write("**[Output Parameters]**")
            new_connections = []
            for arg in source_api.get("output_params", []):
                st.write(
                    f"- **<span style='color: red;'>{arg.get('name', 'Error')}</span>** ({arg.get('type', '')}): {arg.get('description', '')}",
                    unsafe_allow_html=True,
                )
                input_options = [param["name"] for param in target_api.get("input_params", [])] + ["None"]
                selected = [
                    conn["target_arg"]
                    for conn in st.session_state.temp_connections
                    if conn and conn["source_arg"] == arg["name"]
                ]
                checkbox_states = {}
                for input_arg in input_options:
                    checkbox_label = (
                        "None of the above"
                        if input_arg == "None"
                        else f"Compatible with **'{input_arg}'** of Target API's input parameters"
                    )
                    is_checked = input_arg in selected
                    checkbox_key = f"{st.session_state.current_pair}_{arg['name']}_{input_arg}"
                    checkbox_states[input_arg] = st.checkbox(checkbox_label, value=is_checked, key=checkbox_key)
                for input_arg, checked in checkbox_states.items():
                    if checked:
                        new_connections.append(
                            {
                                "source": source_api.get("name", ""),
                                "source_arg": arg.get("name"),
                                "target": target_api.get("name", ""),
                                "target_arg": input_arg,
                            }
                        )
            st.session_state.temp_connections = new_connections

    # Target API 표시
    with col2:
        with st.container(height=700):
            st.write("#### Target API")
            st.write(
                f"**<span style='color: blue;'>{target_api.get('name', 'Error')}</span>** : {target_api.get('description', '')}",
                unsafe_allow_html=True,
            )
            st.write("\n")
            st.write("**[Input Parameters]**")
            target_input_params = target_api.get("input_params", [])
            if target_input_params:
                target_input_data = [
                    {
                        "Parameter Name": arg.get("name", "Error"),
                        "Type": arg.get("type", ""),
                        "Description": arg.get("description", ""),
                    }
                    for arg in target_input_params
                ]
                df_target_input = pd.DataFrame(target_input_data)
                st.table(df_target_input)
            st.write("**[Output Parameters]**")
            for arg in target_api.get("output_params", []):
                st.write(f"- **{arg.get('name', 'Error')}** ({arg.get('type', '')}): {arg.get('description', '')}")

    st.divider()

    # 페이지 이동 컨트롤
    _, left, middle, right, _ = st.columns(5)
    if st.session_state.current_pair > 0 and left.button("◀️ Previous", use_container_width=True):
        previous_page()
        st.rerun()

    source_output_params = [arg.get("name") for arg in source_api.get("output_params", [])]
    if st.session_state.current_pair < len(group_pairs) - 1:
        if right.button("Next ▶️", use_container_width=True):
            if all(
                any(conn["source_arg"] == source_arg for conn in new_connections)
                for source_arg in source_output_params
            ):
                st.session_state.show_warning = False
                next_page(api_pairs_grouped)
                st.rerun()
            else:
                st.session_state.show_warning = True

    if st.session_state.current_pair == len(group_pairs) - 1:
        if right.button("**Finish Annotation 🏁**", use_container_width=True):
            if all(
                any(conn["source_arg"] == source_arg for conn in new_connections)
                for source_arg in source_output_params
            ):
                save_connections()
                annotation_result = []
                for conn in st.session_state.connections.values():
                    for c in conn:
                        if c.get("target_arg", "") != "None":
                            annotation_result.append(c)
                annotator_prolific_id = st.session_state.prolific_id.strip()
                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                with open(f"./annotation_result/{annotator_prolific_id}_{now}.json", "w") as outfile:
                    json.dump(annotation_result, outfile, indent=4)
                st.session_state.page = "finish"
                st.rerun()
            else:
                st.session_state.show_warning = True

    if st.session_state.show_warning:
        st.warning("⚠️ You must check at least one checkbox for each output parameter in the source API to proceed.")

    middle.write(
        f"<div style='text-align: center;'>Page {st.session_state.current_pair + 1} of {len(group_pairs)}</div>",
        unsafe_allow_html=True,
    )


def render_finish_page():
    """어노테이션 완료 후 완료 페이지를 렌더링합니다."""
    st.title("Annotation Completed 🎉")
    st.divider()
    st.write("Thank you for completing the task.")
    st.write("Your annotations have been saved successfully.")
