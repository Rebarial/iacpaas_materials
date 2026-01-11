import requests
from .fefu_cluster_auth_key_placeholder import auth_key


def get_prompt_fefu_cluster(text, auth_token, model_name):
    return {
        "auth_token": f"{auth_token}",
        "model_name": f"{model_name}",

        "conversation": [
            {
            "role": "user",
            "content": f"{text}"
            }
        ],
        "generation_config":
        {
            "temperature": 0.01,
            "max_new_tokens": 8000,
            "max_length": 300,
            "max_time": 120,
            "repetition_penalty": 1.00,
            "top_p": 1,
            "top_k": 60
        }
    }

def send_request_fefu_cluster(prompt, generate_url):
    response = requests.post(generate_url, json=prompt, timeout=1200)
    print(response)
    if response.status_code == 200:
        if "exception" in response.json():
            print(response.json()["exception"])
        else:
            response_text = response.json()["output"]
            print(response_text)
            return response_text

config_fefu_cluster_qwen_3_4b = {
    "name": "fefu_cluster_qwen_3_4b",
    "url": "https://llm.iacpaas.dvo.ru/api/inference",
    "prompt_template": get_prompt_fefu_cluster,
    "model_name": "qwen_3_4b",
    "key": auth_key,
    "send_request": send_request_fefu_cluster,
}

config_fefu_cluster_gemma_3_27b = {
    "name": "fefu_cluster_gemma_3_27b",
    "url": "https://llm.iacpaas.dvo.ru/api/inference",
    "prompt_template": get_prompt_fefu_cluster,
    "model_name": "gemma_3_27b",
    "key": auth_key,
    "send_request": send_request_fefu_cluster,
}