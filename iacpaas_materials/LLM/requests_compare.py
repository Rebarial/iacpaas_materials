import json


def get_prompt_text_compare_responses(properties_template, responses):
    return f"""Сравни следующие наборы характеристик на ошибки:
    {json.dumps(responses)}

    Построй набор характеристик на их основе в данном формате JSON:
    {json.dumps(properties_template)}

    Если информация в ответах для характеристики расходится, заполни её символом '?'.
    Числовые значения должны быть заполнены с единицами измерения."""


def LLM_generate_compare_responses(responses, properties_template, config):
    input = get_prompt_text_compare_responses(properties_template, responses)

    url = config["url"]
    prompt_template = config["prompt_template"]
    model_name = config["model_name"]
    key = config["key"]
    send_request = config["send_request"]

    prompt = prompt_template(input, key, model_name)
    response = send_request(prompt, url)
    return response
