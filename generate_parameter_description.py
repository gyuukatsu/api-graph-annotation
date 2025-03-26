import os
import json

from tqdm import tqdm
from typing import List, Dict
import dotenv
from openai import OpenAI

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")
PROMPT = """
You are a helpful assistant for a developer who is trying to understand the usage of an API.
The developer will provide you with the API name, description, input parameters, and output parameters.
Your job is to generate a description for specific output parameters of the API.
The description should help the developer understand the information that the output parameter provides.
The description must be concise.
Do not generate information that is not present in the API documentation.
Here are some examples:

USER: {
    "name": "amazon.show_account",
    "description": "Show your account information. Unlike show_profile, this includes private information.",
    "input_params": [
        {
            "name": "access_token",
            "type": "str",
            "description": "Access token obtained from amazon app login.",
            "required": true,
            "default": null,
            "constraints": []
        }
    ],
    "output_params": [
        {
            "name": "first_name",
            "type": "str"
        },
        {
            "name": "last_name",
            "type": "str"
        },
        {
            "name": "email",
            "type": "str"
        },
        {
            "name": "registered_at",
            "type": "str"
        },
        {
            "name": "last_logged_in",
            "type": "str"
        },
        {
            "name": "verified",
            "type": "bool"
        },
        {
            "name": "is_prime",
            "type": "bool"
        }
    ]
}
I need a description for the output parameter "first_name".

ASSISTANT: The first name of the user.

USER: I need a description for the output parameter "last_logged_in".

ASSISTANT: The last time the user logged in.
"""


def generate_arg_description(openai_client: OpenAI, api: Dict, output_param: Dict) -> Dict:
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(api)
                + "\n"
                + 'I need a description for the output parameter "'
                + output_param["name"]
                + '".',
            },
            {
                "role": "assistant",
                "content": "ASSISTANT: ",
            },
        ],
    )
    response = completion.choices[0].message.content
    return response


def main(apis: List[Dict]):
    openai_client = OpenAI(
        organization=ORGANIZATION,
        api_key=OPENAI_API_KEY,
    )
    sampled_apis = []
    for api in tqdm(apis):
        sampled_apis.append(api)
        for idx, output_param in enumerate(api["output_params"]):
            arg_description = generate_arg_description(openai_client, api, output_param)
            print(f"[API] {api['name']} : {api['description']}")
            print(f"[Output Param] {output_param['name']}")
            print(arg_description)
            print()
            sampled_apis[-1]["output_params"][idx]["description"] = arg_description

    json.dump(sampled_apis, open("./preprocessed_data/appworld_apis_with_generated_description.json", "w"), indent=2)


if __name__ == "__main__":
    apis = json.load(open("../data/appworld/apis_for_annotation.json"))
    main(apis)
