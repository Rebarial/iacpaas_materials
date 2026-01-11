from django.shortcuts import render
import json
import os
from django.conf import settings
from iacpaas_materials.materials_parser.link_collector import process_and_save_source

from iacpaas_materials.LLM.requests import LLM_generate_for_extracted_data, configs

from django.http import JsonResponse


def get_parser_config():
    with open(os.path.join(settings.BASE_DIR, 'iacpaas_materials/materials_parser/parser_config.json'), 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def get_links_data():
    with open("product_links.json", 'r', encoding='utf-8') as f:
        links = json.load(f)
    return links


def choice_link(request):
    config = get_parser_config()

    sources = [
        {
            'name': source['name'],
            'id': str(index)  # индекс как строка: "0", "1", и т.д.
        }
        for index, source in enumerate(config['sources'])
    ]

    return render(request, 'process/choice_link.html', {'sources': sources})

def choice_materials(request):
    source_id = request.GET.get('source')
    if not source_id or not source_id.isdigit():
        source_id = 0
    else:
        source_id = int(source_id)

    config = get_parser_config()
    source_data = config["sources"][source_id]

    preload = request.GET.get('preload')

    if not preload:
        process_and_save_source(source_data, "product_links.json")


    links = get_links_data()["sources"][0]["product_links"]

    # Добавляем временный ID к каждой ссылке для удобства
    for idx, link in enumerate(links):
        link['id'] = idx

    return render(request, 'process/choice_materials.html', {
        'source_name': source_data['name'],
        'links': links,
        'source_id': source_id
    })

def llm_parsing(request):
    data = get_links_data()
    source = data["sources"][0]

    if request.method == "POST":
        selected_ids = set(int(x) for x in request.POST.getlist("selected_links"))
        filtered_links = [
            link for idx, link in enumerate(source["product_links"])
            if idx in selected_ids
        ]
        source["product_links"] = filtered_links

        json_path = os.path.join(settings.BASE_DIR, 'temp_llm_result.json')

        use_preload = 'use_preload' in request.POST

        if use_preload:
            with open(json_path, 'r', encoding='utf-8') as f:
                result = json.load(f)

        else:
            result = LLM_generate_for_extracted_data(data, configs)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        # Извлекаем только нужные данные (список продуктов)
        products = result[0]['product_links']  # Это список словарей

        rs = []

        for re in products:
            rs.append(re["response"])

        # Передаём в шаблон
        return render(request, "process/parsing_result.html", {"products": rs})

    # Если GET — можно показать ошибку или редирект
    return render(request, "process/parsing_result.html", {"products": []})
