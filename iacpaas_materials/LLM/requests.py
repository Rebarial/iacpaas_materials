import json

from .fefu_cluster import *


configs = {
    # "qwen": config_fefu_cluster_qwen_3_4b,
    "gemma": config_fefu_cluster_gemma_3_27b
}

def get_prompt_text(properties_template, input_text):
    return "Извлеки информацию из текста в следующий формат JSON (Если необходимая информация отсутствует, вставь в поле символ '?'):" \
    "" \
    f"{properties_template}" \
    "" \
    "Текст:" \
    "" \
    f"{input_text}"

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

def LLM_generate_for_extracted_data(data, properties_template, configs):
    sources = data['sources']
    for source in sources:
        product_links = source['product_links']
        for product_link in product_links:
            soup = product_link['soup']
            text = product_link['text']
            responses = []
            responses += LLM_generate_multiple(soup, properties_template, configs)
            responses += LLM_generate_multiple(text, properties_template, configs)
            product_link['responses'] = responses
    return sources

def compare_responses(responses, properties_template):
    # Парсим ответы от llm, если возможно
    parsed_responses = []
    for response in responses:
        response_str = str(response)
        istart = response_str.index("{") if "{" in response_str else -1
        iend = response_str.index("}") if "}" in response_str else -1
        if (istart < iend and istart != -1 and iend != -1):
            parsed_response = response_str[istart:iend + 1]
            try:
                parsed_response = json.loads(parsed_response)
                # print(parsed_response)
                parsed_responses.append(parsed_response)
            except:
                print("Неверный формат")
        else:
            print("Неверный формат")

    # Сравниваем ответы, отсеиваем несовпадающие характеристики
    verified_response = {}
    for key in properties_template.keys():
        value = None
        valid = True
        for response in parsed_responses:
            if (not (key in response) or response[key] == -1 or (value != None and response[key] != value)):
                valid = False
            elif (key in response):
                value = response[key]
        if (valid and value):
            verified_response[key] = value
        else:
            verified_response[key] = "?"
                
    return verified_response
