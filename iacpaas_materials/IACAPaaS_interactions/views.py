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
        source_id = None  # Не фиксируем на 0, а просто показываем все
    else:
        source_id = int(source_id)

    config = get_parser_config()

    # Получаем все источники или один, если указан source_id
    if source_id is not None and 0 <= source_id < len(config["sources"]):
        sources_to_show = [config["sources"][source_id]]
        source_name = config["sources"][source_id]["name"]
    else:
        sources_to_show = config["sources"]
        source_name = "Все источники"

    preload = request.GET.get('preload')

    if not preload:
        # Если нужно обрабатывать все источники при отсутствии preload — можно цикл добавить
        for src in sources_to_show:
            process_and_save_source(src, "product_links.json")

    # Собираем все ссылки из всех выбранных источников
    all_links = []
    link_id = 0
    for src_idx, source in enumerate(sources_to_show):
        links_data = get_links_data().get("sources", [])
        if src_idx < len(links_data):
            product_links = links_data[src_idx].get("product_links", [])
        else:
            product_links = []

        for link in product_links:
            link = link.copy()  # чтобы не менять оригинал
            link['id'] = link_id
            link['source_name'] = source['name']
            link['source_id'] = src_idx if source_id is None else source_id
            all_links.append(link)
            link_id += 1

    # Фильтрация по type и name (через GET-параметры)
    filter_type = request.GET.get('filter_type', '').strip()
    filter_name = request.GET.get('filter_name', '').strip()

    if filter_type:
        all_links = [l for l in all_links if l.get('type', '') == filter_type]
    if filter_name:
        all_links = [l for l in all_links if filter_name.lower() in l.get('link', '').lower()]

    return render(request, 'process/choice_materials.html', {
        'source_name': source_name,
        'links': all_links,
        'source_id': source_id,
        'filter_type': filter_type,
        'filter_name': filter_name,
        'all_types': sorted(set(l.get('type', '') for l in all_links if l.get('type'))),
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
            component_name = comp.get("component_formula", "").strip()
            designation_type_name = comp.get("designation_type", "").strip()
            percent_value = comp.get("percent_value", "").strip().replace(",", ".")
            percent_value = re.sub(r'[^0-9.,?]', '', percent_value)

            if not (component_name and designation_type_name):
                continue

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

from django.db.models import Q

def gas_list(request):
    # Определяем, включён ли фильтр
    show_with_question = request.GET.get('with_question') == '1'

    gases = Gas.objects.select_related().prefetch_related(
        'chemicaldesignation_set__component',
        'chemicaldesignation_set__designation_type'
    )

    if show_with_question:
        # Фильтруем по полям Gas
        gas_fields_with_q = Q(
            name_gas__contains='?',
        ) | Q(formula__contains='?') | Q(grade__contains='?') | \
            Q(brand__contains='?') | Q(standard__contains='?') | \
            Q(adress_gas__contains='?')

        # Фильтруем по связанным ChemicalDesignation
        cd_fields_with_q = Q(
            chemicaldesignation__component__formula__contains='?'
        ) | Q(chemicaldesignation__designation_type__name__contains='?') | \
           Q(chemicaldesignation__percent_value__contains='?')

        # Но percent_value — float, и '?' там быть не может, так что игнорируем его
        # Однако, если вы где-то храните '?' как строку вместо числа — уточните.
        # Пока исключаем percent_value из проверки на '?'

        # Ищем газы, у которых есть '?' в основных полях ИЛИ в связанных
        gases = gases.filter(gas_fields_with_q | cd_fields_with_q).distinct()

    return render(request, 'gases/gas_list.html', {'gases': gases, 'show_with_question': show_with_question})

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
from ..IACPaaS_api.serialize_gas import Gas_serialize
from ..IACPaaS_api.api_config import acount_login, acount_password, default_path
from .serialize import gases_to_iacpaas_dicts

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
        username = os.getenv('IACPAAS_USERNAME', acount_login)
        password = os.getenv('IACPAAS_PASSWORD', acount_password)

        if not password:
            raise ValueError("Пароль IACPaaS не задан в переменных окружения")

        # Авторизация через connection.py
        api_key = signin(username, password)
        if not api_key:
            raise Exception("Не удалось получить токен доступа")

        gas_serialize = Gas_serialize()
        json_data = Gas_serialize()

        # Сериализация
        gases_dict = gases_to_iacpaas_dicts(gases)
        gas_serialize = Gas_serialize()
        gas_serialize.add_elements(gases_dict)

        json_payload = gas_serialize.get_json()

        # Отправка через connection.py
        result = import_resource(
            API_KEY=api_key,
            path=default_path,
            json=json_payload,
            clearIfExists=True
        )

        print(result)

        if result.get('success'):
            messages.success(request, f"Успешно отправлено {gases.count()} газ(ов) в IACPaaS.")
        else:
            messages.error(request, f"Ошибка IACPaaS: {result.get('message', result)}")

    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")

    return redirect('iacpaas:gas_list')
