import json

from .fefu_cluster import *
from .property_templates import property_type_dic
from .response_comparison import compare_responses

configs = {
    # "qwen": config_fefu_cluster_qwen_3_4b,
    "gemma": config_fefu_cluster_gemma_3_27b
}

def get_prompt_text(properties_template, input_text):
    return f"""Извлеки информацию из текста в данный формат JSON:
    {json.dumps(properties_template)}

    Если необходимая информация отсутствует, вставь в поле символ '?'.
    Числовые значения должны быть заполнены с единицами измерения.

    Текст:
    {input_text}"""

def LLM_generate(input_text, properties_template, config):
    input = get_prompt_text(properties_template, input_text)

    url = config["url"]
    prompt_template = config["prompt_template"]
    model_name = config["model_name"]
    key = config["key"]
    send_request = config["send_request"]

    prompt = prompt_template(input, key, model_name)
    response = send_request(prompt, url)
    return response

def LLM_generate_multiple(input_text, properties_template, configs):
    attempts_per_config = 1

    responses = []
    for config in configs.values():
        for i in range(attempts_per_config):
            responses.append(LLM_generate(input_text, properties_template, config))
    return responses

def LLM_generate_for_extracted_data(data, configs):
    sources = data
    for product_link in sources:
        type = product_link['type']
        properties_template = property_type_dic[type]
        soup = product_link['soup']
        text = product_link['text']
        responses = []
        # responses += LLM_generate_multiple(soup, properties_template, configs)
        responses += LLM_generate_multiple(soup, properties_template, configs)
        responses += LLM_generate_multiple(soup, properties_template, configs)
        response = compare_responses(responses, properties_template)
        print(responses)
        response['link'] = product_link['link']
        response['type'] = type
        product_link['response'] = response
        product_link.pop('soup', None)
        product_link.pop('text', None)
    return sources

