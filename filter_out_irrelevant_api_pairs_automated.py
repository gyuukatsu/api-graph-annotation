from typing import List, Dict
import json
from tqdm import tqdm
import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def filter_out_irrelevant_api_pairs(data, threshold=0.3):
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 각 API의 output, input 파라미터 description을 별도 리스트에 저장하고, 글로벌 인덱스를 기록
    output_desc_list = []  # 모든 API의 output parameter description
    input_desc_list = []  # 모든 API의 input parameter description
    output_api_mapping = {}  # key: API index, value: output_desc_list 내 해당 API의 파라미터 인덱스 리스트
    input_api_mapping = {}  # key: API index, value: input_desc_list 내 해당 API의 파라미터 인덱스 리스트

    for api_idx, api in enumerate(data):
        output_params = api.get("output_params", [])
        for param in output_params:
            desc = param.get("description", "")
            if desc:  # description이 있을 때만
                output_api_mapping.setdefault(api_idx, []).append(len(output_desc_list))
                output_desc_list.append(desc)

        input_params = api.get("input_params", [])
        for param in input_params:
            desc = param.get("description", "")
            if desc:
                input_api_mapping.setdefault(api_idx, []).append(len(input_desc_list))
                input_desc_list.append(desc)

    # 미리 한 번에 임베딩 계산 (각각 output, input 파라미터에 대해)
    if output_desc_list:
        output_embs = model.encode(output_desc_list, show_progress_bar=True)
    else:
        output_embs = np.array([])

    if input_desc_list:
        input_embs = model.encode(input_desc_list, show_progress_bar=True)
    else:
        input_embs = np.array([])

    # output과 input 임베딩 간 cosine similarity 행렬 계산 (행: output 파라미터, 열: input 파라미터)
    if output_embs.size and input_embs.size:
        sim_matrix = cosine_similarity(output_embs, input_embs)
    else:
        sim_matrix = np.array([])

    relevant_api_pairs = []
    irrelevant_api_pairs = []

    # API pair 단위로 global 행렬에서 해당하는 행, 열을 슬라이싱하여 threshold를 넘는지 확인
    for src_api_idx, source_api in enumerate(data):
        # source API에 output 파라미터의 description이 없으면, similarity 비교 불가로 간주
        if src_api_idx not in output_api_mapping:
            for tgt_api_idx, target_api in enumerate(data):
                if src_api_idx == tgt_api_idx:
                    continue
                irrelevant_api_pairs.append((source_api, target_api))
            continue

        src_indices = output_api_mapping[src_api_idx]
        for tgt_api_idx, target_api in enumerate(data):
            if src_api_idx == tgt_api_idx:
                continue

            if tgt_api_idx not in input_api_mapping:
                irrelevant_api_pairs.append((source_api, target_api))
                continue

            tgt_indices = input_api_mapping[tgt_api_idx]

            # 슬라이싱: np.ix_를 사용하면, output 파라미터 인덱스와 input 파라미터 인덱스에 해당하는 submatrix 추출
            submatrix = sim_matrix[np.ix_(src_indices, tgt_indices)]
            if (submatrix > threshold).any():
                relevant_api_pairs.append((source_api, target_api))
            else:
                irrelevant_api_pairs.append((source_api, target_api))

    return relevant_api_pairs, irrelevant_api_pairs


if __name__ == "__main__":
    datasets = ["nestful", "nestools", "appworld"]
    for dataset in datasets:
        print("Processing", dataset)
        with open(f"../data/{dataset}/apis_for_annotation.json", "r") as f:
            data = json.load(f)
        relevant_api_pairs, irrelevant_api_pairs = filter_out_irrelevant_api_pairs(data)

        with open(f"./preprocessed_data/{dataset}_relevant_api_pairs.json", "w") as f:
            json.dump(relevant_api_pairs, f, indent=2)
        with open(f"./preprocessed_data/{dataset}_irrelevant_api_pairs.json", "w") as f:
            json.dump(irrelevant_api_pairs, f, indent=2)
