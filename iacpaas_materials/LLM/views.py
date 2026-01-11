from django.shortcuts import render
from iacpaas_materials.LLM.requests import LLM_generate_for_extracted_data, configs
import json
import os
from django.conf import settings
from django.http import JsonResponse

def llm_parsing(request):
    #json.load(open(os.path.join(settings.BASE_DIR, 'tests/product_links.json')))
    #json.load(open(os.path.join(settings.BASE_DIR, 'product_links.json')))
    data = json.load(open(os.path.join(settings.BASE_DIR, 'tests/product_links.json')))
    result = LLM_generate_for_extracted_data(data, configs)
    #print(result[0])
    return JsonResponse(result, safe=False, json_dumps_params={'ensure_ascii': False})
