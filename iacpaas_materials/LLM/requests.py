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

    Если необходимая информация отсутствует, вставь в поле символ '-'.
    Числовые значения должны быть заполнены с единицами измерения.
    Извлеки все элементы списков и таблиц в соответствующие списки.

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
        text = product_link['text']
        responses = []

        responses += LLM_generate_multiple(text, properties_template, configs)
        responses += LLM_generate_multiple(text, properties_template, configs)        
        # soup = product_link['soup']
        # optimised_soup = optimise_soup(soup)
        # responses += LLM_generate_multiple(optimised_soup, properties_template, configs)
        # responses += LLM_generate_multiple(optimised_soup, properties_template, configs)
        
        response = compare_responses(responses, properties_template)
        print(responses)
        for key in response.keys():
            product_link[key] = response[key]
        product_link.pop('soup', None)
        product_link.pop('text', None)
    return sources

def optimise_soup(soup):
    finished = False
    while ("class=\"" in soup and soup.count("\"") >= 2):
        istart = soup.find("class=\"")
        a = soup[:istart]
        b = soup[istart:]
        iend = soup.find("\"")
        c = b[(iend + 1):]
        soup = a + c
    print(soup)
    return soup