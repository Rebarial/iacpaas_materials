from django.shortcuts import render
from iacpaas_materials.LLM.requests import LLM_generate_for_extracted_data, configs
import json
import os
from django.conf import settings
from django.http import JsonResponse
from iacpaas_materials.materials_parser.link_collector import process_and_save_source

def llm_parsing(request):
    #json.load(open(os.path.join(settings.BASE_DIR, 'tests/product_links.json')))
    #json.load(open(os.path.join(settings.BASE_DIR, 'product_links.json')))
    parser_config = json.load(open(os.path.join(settings.BASE_DIR, 'iacpaas_materials/materials_parser/parser_config.json')))
    print(parser_config)
    print('parsers')
    process_and_save_source(parser_config["sources"][0], "product_links.json")
    #print(data)##json.load(open(os.path.join(settings.BASE_DIR, 'tests/product_links.json')))
    #result = LLM_generate_for_extracted_data(data, configs)
    #print(result[0])
    #result
    return JsonResponse("hi", safe=False, json_dumps_params={'ensure_ascii': False})
