import pytest
import json
import os
from django.conf import settings

from iacpaas_materials.LLM.requests import LLM_generate, LLM_generate_multiple, configs, LLM_generate_for_extracted_data, compare_responses

input_json = json.load(open(os.path.join(settings.BASE_DIR, 'tests/product_links.json')))
text = input_json["sources"][0]["product_links"][0]["text"]
responses_json = [
    {
        "Name": "Продукт",
        "Description": "Описание",
        "Density": "42",
        "Yield Strength": "24",
        "Thermal Conductivity": "?",
        "Cost": "?",
        "Color": ""
    },
    {
        "Name": "Продукт",
        "Description": "О",
        "Yield Strength": "?",
        "Cost": "?",
        "Color": "Красный"
    }
]
response_validated_json = {
    "Name": "Продукт",
    "Description": "?",
    "Density": "?",
    "Yield Strength": "?",
    "Thermal Conductivity": "?",
    "Cost": "?",
    "Color": "?"
}
properties_template = {
    "Name": "",
    "Description": "",
    "Density": "",
    "Yield Strength": "",
    "Thermal Conductivity": "",
    "Cost": "",
    "Color": ""
}


@pytest.mark.parametrize(
    ("config"), 
    configs
)
def test_LLM_generate(config):
    response = LLM_generate(text, properties_template, configs[config])
    assert isinstance(response, str)

def test_LLM_generate_multiple():
    responses = LLM_generate_multiple(text, properties_template, configs)
    assert isinstance(responses, list)
    print(responses)
    for response in responses:
        assert isinstance(response, str)

def test_LLM_generate_for_extracted_data():
    sources = LLM_generate_for_extracted_data(input_json, properties_template, configs)
    assert isinstance(sources, list)
    for source in sources:
        product_links = source['product_links']
        for product_link in product_links:
            response = product_link['response']
            assert isinstance(response, dict)

def test_compare_responses():
    response_strings = []
    for response in responses_json:
        response_string = json.dumps(response)
        response_strings.append(response_string)
    result = compare_responses(response_strings, properties_template)
    assert result == response_validated_json

def test_compare_responses_invalid_strings():
    response_strings = []
    for response in responses_json:
        response_string = json.dumps(response)
        response_string = response_string[:1] + ':' + response_string[1:]
        print(response_string)
        response_strings.append(response_string)
    result = compare_responses(response_strings, properties_template)
    assert isinstance(response, dict)
    for value in result.values():
        assert value == "?"