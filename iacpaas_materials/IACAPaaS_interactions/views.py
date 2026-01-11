from django.shortcuts import render
import json
import os
from django.conf import settings
from iacpaas_materials.materials_parser.link_collector import process_and_save_source
from django.shortcuts import get_object_or_404, redirect

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
            'id': str(index)
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

        products = result[0]['product_links']

        rs = []

        for re in products:
            rs.append(re["response"])

        request.session['parsed_products'] = products

        return render(request, "process/parsing_result.html", {"products": rs})

    return render(request, "process/parsing_result.html", {"products": []})

import re
from .models import Gas, ChemicalComponent, ChemicalDesignationType, ChemicalDesignation
from django.shortcuts import redirect
from django.contrib import messages

from django.shortcuts import redirect
from django.contrib import messages
import re
from .models import Gas, ChemicalComponent, ChemicalDesignationType, ChemicalDesignation

from django.shortcuts import redirect
from django.contrib import messages
import re
from .models import Gas, ChemicalComponent, ChemicalDesignationType, ChemicalDesignation


def save_selected_gases(request):
    if request.method != "POST":
        return redirect('iacpaas:llm_parsing')

    selected_indices = request.POST.getlist("selected_products")
    print(selected_indices)

    if not selected_indices:
        messages.error(request, "Не выбрано ни одного продукта.")
        return redirect('iacpaas:llm_parsing')

    products = request.session.get('parsed_products', [])

    print(products)
    if not products:
        messages.error(request, "Нет данных для сохранения.")
        return redirect('iacpaas:llm_parsing')

    saved_count = 0

    for idx_str in selected_indices:
        try:
            idx = int(idx_str)
            product = products[idx]
        except (ValueError, IndexError, KeyError):
            continue

        adress_gas_val = product["link"]
        product = product["response"]

        name_gas_val = product.get("name", "").strip() or "Без названия"
        grade_val = product.get("grade", "").strip() or "N/A"
        brand_val = product.get("brand", "").strip() or "N/A"

        # Удаляем старые записи (и автоматически — все связанные ChemicalDesignation из-за on_delete=CASCADE)
        Gas.objects.filter(
            name_gas=name_gas_val,
            adress_gas=adress_gas_val,
            grade=grade_val,
            brand=brand_val
        ).delete()

        # === 2. Создаём НОВЫЙ газ ===
        gas = Gas.objects.create(
            name_gas=name_gas_val,
            formula=product.get("formula", "").strip() or "N/A",
            grade=grade_val,
            brand=brand_val,
            standard=product.get("standard", "").strip() or "N/A",
            adress_gas=adress_gas_val,
        )

        # === 3. Создаём новый химический состав ===
        for comp in product.get("chemical_designations", []):
            component_name = comp.get("component", "").strip()
            designation_type_name = comp.get("designation_type", "").strip()
            percent_str = comp.get("percent_value", "").strip()

            if not (component_name and designation_type_name):
                continue

            # Извлекаем числовое значение
            percent_value = 0.0
            cleaned = percent_str.replace(',', '.').lower()
            match = re.search(r'[\d.]+', cleaned)
            if match:
                try:
                    percent_value = float(match.group())
                except ValueError:
                    pass

            component, _ = ChemicalComponent.objects.get_or_create(formula=component_name)
            designation_type, _ = ChemicalDesignationType.objects.get_or_create(name=designation_type_name)

            ChemicalDesignation.objects.create(
                gas=gas,
                component=component,
                designation_type=designation_type,
                percent_value=percent_value
            )

        saved_count += 1

    messages.success(request, f"Успешно сохранено (с заменой) {saved_count} газов.")
    request.session.pop('parsed_products', None)
    return redirect('iacpaas:gas_list')  # или другая страница



def gas_list(request):
    gases = Gas.objects.select_related().prefetch_related(
        'chemicaldesignation_set__component',
        'chemicaldesignation_set__designation_type'
    ).all()
    return render(request, 'gases/gas_list.html', {'gases': gases})

def delete_gas(request, gas_id):
    if request.method == "POST":
        gas = get_object_or_404(Gas, id=gas_id)
        gas_name = gas.name_gas
        gas.delete()
        messages.success(request, f"Газ '{gas_name}' успешно удалён.")
    return redirect('iacpaas:gas_list')


from django.shortcuts import redirect
from django.contrib import messages
from .models import Gas

import os
from django.shortcuts import redirect
from django.contrib import messages
from .models import Gas

from ..IACPaaS_api.api_connection import signin, import_resource
from .serialize import serialize_gases_to_iacpaas_json

def send_to_iacpaas(request):
    if request.method != "POST":
        return redirect('iacpaas:gas_list')

    selected_ids = request.POST.getlist('selected_gases')
    if not selected_ids:
        messages.warning(request, "Не выбрано ни одного газа для отправки.")
        return redirect('iacpaas:gas_list')

    gases = Gas.objects.filter(id__in=selected_ids)
    if not gases.exists():
        messages.error(request, "Выбранные газы не найдены.")
        return redirect('iacpaas:gas_list')

    try:
        username = os.getenv('IACPAAS_USERNAME', 'iagolnitckii.si@dvfu.ru')
        password = os.getenv('IACPAAS_PASSWORD', 'шфсзффышф')

        if not password:
            raise ValueError("Пароль IACPaaS не задан в переменных окружения")

        # Авторизация через connection.py
        api_key = signin(username, password)
        if not api_key:
            raise Exception("Не удалось получить токен доступа")

        # Сериализация
        json_payload = serialize_gases_to_iacpaas_json(gases, base_name="Газы из Django")

        # Отправка через connection.py
        result = import_resource(
            API_KEY=api_key,
            path="Газы",
            json=json_payload,
            clearIfExists=False
        )

        if result.get('code') == 200:
            messages.success(request, f"Успешно отправлено {gases.count()} газ(ов) в IACPaaS.")
        else:
            messages.error(request, f"Ошибка IACPaaS: {result.get('message', result)}")

    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")

    return redirect('iacpaas:gas_list')
