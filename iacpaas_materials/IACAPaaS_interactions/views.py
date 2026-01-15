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

from iacpaas_materials.LLM.property_templates import property_type_dic

def choice_materials(request):
    # Получаем список выбранных source_id
    source_ids = request.GET.getlist('sources')
    preload = request.GET.get('preload')

    config = get_parser_config()
    all_sources = config["sources"]

    # Валидация и преобразование ID в целые числа
    valid_source_ids = []
    for sid in source_ids:
        if sid.isdigit():
            sid_int = int(sid)
            if 0 <= sid_int < len(all_sources):
                valid_source_ids.append(sid_int)

    # Если ничего не выбрано — показываем все
    if not valid_source_ids:
        valid_source_ids = list(range(len(all_sources)))

    # Формируем список источников для обработки
    sources_to_show = [all_sources[i] for i in valid_source_ids]

    # Предзагрузка: вызываем process_and_save_source только если preload НЕ задан
    if not preload:
        for src in sources_to_show:
            process_and_save_source(src, "product_links.json")

    # Сбор всех ссылок из выбранных источников
    all_links = []
    link_id = 0
    links_data = get_links_data().get("sources", [])

    for src_idx in valid_source_ids:
        source = all_sources[src_idx]
        if src_idx < len(links_data):
            product_links = links_data[src_idx].get("product_links", [])
        else:
            product_links = []

        for link in product_links:
            link = link.copy()
            link['id'] = link_id
            link['source_name'] = source['name']
            link['source_id'] = src_idx
            all_links.append(link)
            link_id += 1

    # Фильтрация
    filter_type = request.GET.get('filter_type', '').strip()
    filter_name = request.GET.get('filter_name', '').strip()

    if filter_type:
        all_links = [l for l in all_links if l.get('type', '') == filter_type]
    if filter_name:
        all_links = [l for l in all_links if filter_name.lower() in l.get('link', '').lower()]

    return render(request, 'process/choice_materials.html', {
        'source_name': ', '.join(s['name'] for s in sources_to_show) if len(sources_to_show) < 5 else f"{len(sources_to_show)} источников",
        'links': all_links,
        'source_ids': valid_source_ids,  # можно использовать для обратной связи
        'filter_type': filter_type,
        'filter_name': filter_name,
        'all_types': property_type_dic.keys(),
    })

import os
import json
from django.conf import settings
from django.shortcuts import render

def llm_parsing(request):
    data = get_links_data()  # {'sources': [{'name': ..., 'product_links': [...]}, ...]}
    sources = data.get("sources", [])

    if request.method == "POST":
        # Получаем список глобальных ID, выбранных пользователем
        selected_global_ids = set(int(x) for x in request.POST.getlist("selected_links"))
        use_preload = 'use_preload' in request.POST

        # === Шаг A: Построим маппинг глобальный_id → (source_idx, local_idx) ===
        global_id_to_ref = {}
        current_id = 0
        for src_idx, source in enumerate(sources):
            for local_idx in range(len(source.get("product_links", []))):
                global_id_to_ref[current_id] = (src_idx, local_idx)
                current_id += 1

        # === Шаг B: Соберём только выбранные ссылки по источникам ===
        new_sources = []
        for src_idx, source in enumerate(sources):
            # Извлекаем product_links, но только те, чей глобальный ID выбран
            filtered_links = []
            for local_idx, link in enumerate(source.get("product_links", [])):
                global_id = next(gid for gid, (si, li) in global_id_to_ref.items() if si == src_idx and li == local_idx)
                if global_id in selected_global_ids:
                    filtered_links.append(link)
            # Создаём новый источник с отфильтрованными ссылками
            new_source = {**source, "product_links": filtered_links}
            new_sources.append(new_source)

        # Обновляем данные для LLM
        filtered_data = {"sources": new_sources}

        # === Шаг C: Запуск LLM или загрузка из файла ===
        json_path = os.path.join(settings.BASE_DIR, 'temp_llm_result.json')

        if use_preload and os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            result = LLM_generate_for_extracted_data(filtered_data, configs)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        # === Шаг D: Подготовка результата для отображения ===
        products = result[0].get('product_links', []) if result else []
        rs = [re.get("response", "") for re in products]

        request.session['parsed_products'] = products
        print(products)

        return render(request, "process/parsing_result.html", {"products": rs})

    # GET-запрос — просто показываем пустой результат
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
