import json
import os


def load_api_pairs(file_path: str, pairs_per_group: int):
    """JSON 파일에서 API 쌍을 로드하고 그룹별로 나눕니다."""
    with open(file_path, "r") as f:
        api_pairs = json.load(f)
    api_pairs_grouped = [api_pairs[i : i + pairs_per_group] for i in range(0, len(api_pairs), pairs_per_group)]
    return api_pairs_grouped


def load_mapping(mapping_file: str):
    """매핑 파일이 존재하면 로드하고, 없으면 빈 딕셔너리를 반환합니다."""
    if os.path.exists(mapping_file):
        with open(mapping_file, "r") as f:
            mapping = json.load(f)
    else:
        mapping = {}
    return mapping


def prepare_annotation_pairs(file_path: str, pairs_per_group=100):
    """JSON 파일에서 API 쌍을 로드하고 그룹별로 나눕니다."""
    api_pairs_grouped = load_api_pairs(file_path, pairs_per_group)

    related_pair = json.load(open("./preprocessed_data/quality_check_related_api_pairs.json"))
    unrelated_pair = json.load(open("./preprocessed_data/quality_check_unrelated_api_pairs.json"))

    for group in api_pairs_grouped:
        duplicate_pair = group[5]
        group.insert(25, duplicate_pair)
        group.insert(35, related_pair)
        group.insert(45, unrelated_pair)

    return api_pairs_grouped
