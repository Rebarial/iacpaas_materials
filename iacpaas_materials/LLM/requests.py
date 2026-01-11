import json

from .fefu_cluster import *
from .property_templates import property_type_dic

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
    sources = data['sources']
    for source in sources:
        product_links = source['product_links']
        for product_link in product_links:
            type = product_link['type']
            properties_template = property_type_dic[type]
            soup = product_link['soup']
            text = product_link['text']
            responses = []
            # responses += LLM_generate_multiple(soup, properties_template, configs)
            responses += LLM_generate_multiple(text, properties_template, configs)
            responses += LLM_generate_multiple(text, properties_template, configs)
            response = compare_responses(responses, properties_template)
            print(responses)
            product_link['response'] = response
    return sources

def compare_responses(responses, properties_template):
    # Парсим ответы от llm, если возможно
    parsed_responses = []
    for response in responses:
        response_str = str(response)
        istart = response_str.find("{") if "{" in response_str else -1
        iend = response_str.rfind("}") if "}" in response_str else -1
        if (istart < iend and istart != -1 and iend != -1):
            parsed_response = response_str[istart:iend + 1]
            try:
                parsed_response = json.loads(parsed_response)
                # print(parsed_response)
                parsed_responses.append(parsed_response)
            except:
                print("Неверный формат1")
        else:
            print("Неверный формат2")

    # Сравниваем ответы, отсеиваем несовпадающие характеристики
    return compare_properties(parsed_responses, properties_template)
    
def compare_properties(responses, properties_template):
    verified_response = {}
    for key in properties_template.keys():
        if isinstance(properties_template[key], list):
            if [((key in response) and isinstance(response[key], list)) for response in responses]:
                verified_response[key] = []
                min_list_len = min([len(response[key]) for response in responses])
                for i in range(min_list_len):
                    item_properties_template = properties_template[key][0]
                    item_responses = []
                    for response in responses:
                        if len(response[key]) > i and isinstance(response[key][i], dict):
                            item_responses.append(response[key][i])
                    verified_response[key].append(compare_properties(item_responses, item_properties_template))
            else:
                verified_response[key] = "?"
        else:
            value = None
            valid = True
            for response in responses:
                if (not (key in response) or response[key] == -1 or ((value != None) and (not compare_text(response[key], value)))):
                    valid = False
                elif (key in response):
                    value = response[key]
            if (valid and value):
                verified_response[key] = value
            else:
                verified_response[key] = "?"
                
    return verified_response

def compare_text(string1, string2):
    words = string1.partition(' ')
    return string2.lower().startswith(words[0].lower())

def all_responses_have_(string1, string2):
    words = string1.partition(' ')
    return string2.lower().startswith(words[0].lower())