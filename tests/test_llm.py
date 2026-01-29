import pytest
import json
import os
from django.conf import settings

from iacpaas_materials.LLM.requests import LLM_generate, LLM_generate_multiple, configs, LLM_generate_for_extracted_data, compare_responses
from iacpaas_materials.IACAPaaS_interactions.models import Gas

input_json = json.load(open(os.path.join(settings.BASE_DIR, 'tests/product_links.json')))
# text = input_json["sources"][0]["product_links"][0]["text"]
text = input_json[0]["text"]
# responses_json = [
#     {
#         "Name": "Продукт",
#         "Description": "Описание",
#         "Density": "42",
#         "Yield Strength": "24",
#         "Thermal Conductivity": "?",
#         "Cost": "?",
#         "Color": ""
#     },
#     {
#         "Name": "Продукт",
#         "Description": "О",
#         "Yield Strength": "?",
#         "Cost": "?",
#         "Color": "Красный"
#     }
# ]
# properties_template = {
#     "Name": "",
#     "Description": "",
#     "Density": "",
#     "Yield Strength": "",
#     "Thermal Conductivity": "",
#     "Cost": "",
#     "Color": ""
# }
properties_template = {
    "formula": "",
    "grade": "",
    "brand": "",
    "standard": "",
    "chemical_designations": [
        {
            "component": "",
            "designation_type": "",
            # "percent_min": "",
            # "percent_max": "",
            # "type": "",
        },
    ],
}
responses_json = [
    {
        "formula": "123",
        "grade": "123",
        "brand": "323",
        "standard": "323",
        "chemical_designations": [
            {
                "component": "221",
                "designation_type": "112",
            },
            {
                "component": "221",
            },
            {
                "component": "333",
                "designation_type": "112",
            },
        ],
    },
    {
        "formula": "123",
        "grade": "321",
        "brand": "323",
        "standard": "323",
        "chemical_designations": [
            {
                "component": "221 232",
                "designation_type": "112",
            },
            {
                "component": "333 1",
                "designation_type": "111",
            },
        ],
    }
]
response_validated_json = {
    "formula": "123",
    "grade": "?",
    "brand": "323",
    "standard": "323",
    "chemical_designations": [
        {
            "component": "221 232",
            "designation_type": "112",
            "result_appearance": 1.0,
        },
        {
            "component": "221",
            "designation_type": "?",
            "result_appearance": 0.5,
        },
        {
            "component": "333 1",
            "designation_type": "?",
            "result_appearance": 1.0,
        },
    ],
}


# @pytest.mark.parametrize(
#     ("config"), 
#     configs
# )
# def test_LLM_generate(config):
#     response = LLM_generate(text, properties_template, configs[config])
#     print(response)
#     assert isinstance(response, str)

# def test_LLM_generate_multiple():
#     responses = LLM_generate_multiple(text, properties_template, configs)
#     assert isinstance(responses, list)
#     print(responses)
#     for response in responses:
#         assert isinstance(response, str)

def test_LLM_generate_for_extracted_data():
    sources = LLM_generate_for_extracted_data(input_json, configs)
    assert isinstance(sources, list)
    for source in sources:
        response = source
        assert isinstance(response, dict)
    with open(os.path.join(settings.BASE_DIR, 'tests/data.json'), 'w') as f:
        a = json.dumps(sources)
        a = json.loads(a)
        json.dump(a, f, ensure_ascii=False, indent=4)
    print(sources)
    assert isinstance(sources, list)
    

# def test_compare_responses():
#     response_strings = []
#     for response in responses_json:
#         response_string = json.dumps(response)
#         response_strings.append(response_string)
#     result = compare_responses(response_strings, properties_template)
#     print(result)
#     assert result == response_validated_json

# def test_compare_responses_invalid_strings():
#     response_strings = []
#     for response in responses_json:
#         response_string = json.dumps(response)
#         response_string = response_string[:1] + ':' + response_string[1:]
#         print(response_string)
#         response_strings.append(response_string)
#     result = compare_responses(response_strings, properties_template)
#     assert isinstance(response, dict)
#     for value in result.values():
#         assert value == "?"

# def test_get_template():
#     fields = Gas._meta.get_fields(include_parents=True, include_hidden=False)
#     print(fields)
#     pk = Gas._meta.pk_fields
#     print(pk)
#     for item in fields:
#         if item.is_relation:
#             print(f"{item} - {type(item)} - {item.related_model.__name__}")    
#         else:
#             print(f"{item} - {type(item)} - {item.get_attname()}")    
#     assert isinstance(fields, int)