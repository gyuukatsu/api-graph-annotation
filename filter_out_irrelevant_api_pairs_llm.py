import json
import os

from tqdm import tqdm
import random
from typing import List, Dict
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")

PROMPT = """
You are an assistant who helps developers understand the relevance between two APIs.
The developer will provide you with the documentation of the APIs.
One is the source API, and the other is the target API.
You job is to determine if one of the output params of the source API can be used as an input param to the target API.
Then you need to generate a relevance score between 0 and 1, which indicates the probability of the source API and the target API can be chained together.
You should give observation first, then the relevance score.
You should not consider input params of the source API or output params of the target API.

There are some rules you should consider:
1. Prioritize Parameter Descriptions
Do not rely solely on parameter names to infer their meaning.
Always refer to the parameter description, as names can be misleading.
Example: `username` might actually refer to an email address. The description provides clarity.

2. Complete Information Matching
A source parameter can be linked to multiple target parameters if it contains all necessary information.
Example: `full_name` (source) → `first_name`, `last_name` (target).
However, partial matches are not allowed.
Example: `first_name` (source) cannot be connected to `full_name` (target).

3. Type Compatibility is Flexible
Parameter types do not have to be identical as long as the value meaning is preserved.
Example: If `height` is a string in the source API but an integer in the target API, you can still connect them.

Your output should be a JSON object in the following format. For example:
Source API: 
{
    "name": "TrainSearch",
    "description": "Retrieves available train services.",
    "input_params": [
    // input params (hidden)
    ],
    "output_params": [
        ...
        {
            "name": "originCity",
            "type": "str",
            "description": "The city where the train journey begins."
        },
        ...
    ]
}
Target API:
{
    "name": "SearchLocation",
    "description": "Searches for a location using a keyword.",
    "input_params": [
        ...
        {
            "name": "query",
            "type": "str",
            "description": "The keyword to search for. (e.g., city name)"
        },
        ...
    ],
    "output_params": [
        // output params (hidden)
    ]
}
Output:
{
    "source": "source_api_name",
    "target": "target_api_name",
    "observation": "It seems that the output param 'originCity' of the source API can be used as an input param 'query' of the target API, as they both refer to the location information. But the relevance score is low because the source API is about train services, while the target API is about location search.",
    "relevance_score": 0.5
}
Don't say anything else, just provide the JSON object like above.
"""


def get_relevance_score(openai_client, source_api, target_api) -> Dict:
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": PROMPT,
            },
            {
                "role": "user",
                "content": "\n".join(
                    [
                        "Source API:",
                        json.dumps(source_api),
                        "Target API:",
                        json.dumps(target_api),
                    ]
                ),
            },
            {
                "role": "assistant",
                "content": "Output: ",
            },
        ],
    )
    response = completion.choices[0].message.content

    try:
        if "```json" in response:
            output_json = json.loads(response.split("```json")[1].split("```")[0])
        else:
            output_json = json.loads(response)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)

    return output_json


if __name__ == "__main__":
    openai_client = OpenAI(
        organization=ORGANIZATION,
        api_key=OPENAI_API_KEY,
    )

    # datasets = ["nestful", "appworld", "nestools"]
    datasets = ["nestful"]
    for dataset in datasets:
        api_pairs = json.load(open(f"./preprocessed_data/{dataset}_irrelevant_api_pairs.json", "r"))

        # random sample 100 pairs each
        # samples = random.sample(api_pairs, 100)
        relevance_score = []

        for api_pair in tqdm(api_pairs):
            source_api = api_pair[0]
            target_api = api_pair[1]
            source_api["input_params"] = ["// input params (hidden)"]
            target_api["output_params"] = ["// output params (hidden)"]

            output = get_relevance_score(openai_client, source_api, target_api)
            relevance_score.append(output)

        json.dump(
            relevance_score,
            open(f"./preprocessed_data/{dataset}_irrelevant_api_pair_relevance_scores.json", "w"),
            indent=2,
        )
