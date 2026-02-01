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

def get_links():
    with open("iacpaas_materials/materials_parser/product_links.json", 'r', encoding='utf-8') as f:
        links = json.load(f)
    return links

def get_parse_data():
    with open("iacpaas_materials/materials_parser/product_data.json", 'r', encoding='utf-8') as f:
        links = json.load(f)
    return links

config = get_parser_config()
sources = [
    {
        'name': source['name'],
        'id': str(index)
    }
    for index, source in enumerate(config['sources'])
]

def choice_link(request):
    return render(request, 'process/choice_link.html', {'sources': sources})

from iacpaas_materials.LLM.property_templates import property_type_dic

def choice_materials(request):
    source_ids = request.GET.getlist('sources')
    preload = request.GET.get('preload')
    max_pages_raw = request.GET.get('max_pages', '')

    max_pages = int(max_pages_raw) if max_pages_raw.strip().isdigit() else 100

    config = get_parser_config()
    all_sources = config["sources"]

    valid_source_ids = []
    for sid in source_ids:
        if sid.isdigit():
            sid_int = int(sid)
            if 0 <= sid_int < len(all_sources):
                valid_source_ids.append(sid_int)

    if not valid_source_ids:
        valid_source_ids = list(range(len(all_sources)))

    sources_to_show = [all_sources[i] for i in valid_source_ids]

    if not preload:
        for src in sources_to_show:
            process_and_save_source(
                src,
                max_pages=max_pages
            )

    all_links = []
    link_id = 0
    links_data = get_links().get("sources", [])

    for src_idx in valid_source_ids:
        source = all_sources[src_idx]
        if src_idx < len(links_data):
            product_links = links_data[src_idx].get("product_links", [])
        else:
            product_links = []

        for link in product_links:
            link = link.copy()
            all_links.append(link)
            link_id += 1

    filter_type = request.GET.get('filter_type', '').strip()
    filter_name = request.GET.get('filter_name', '').strip()

    if filter_type:
        all_links = [l for l in all_links if l.get('type', '') == filter_type]
    if filter_name:
        all_links = [l for l in all_links if filter_name.lower() in l.get('link', '').lower()]

    return render(request, 'process/choice_materials.html', {
        'source_name': ', '.join(s['name'] for s in sources_to_show) if len(sources_to_show) < 5 else f"{len(sources_to_show)} источников",
        'links': all_links,
        'source_ids': valid_source_ids,
        'filter_type': filter_type,
        'filter_name': filter_name,
        'all_types': property_type_dic.keys(),
        'max_pages': max_pages,
    })
import os
import json
from django.conf import settings
from django.shortcuts import render

def llm_parsing(request):
    data = get_parse_data()

    if request.method == "POST":
        selected_global_ids = request.POST.getlist("selected_links")
        use_preload = 'use_preload' in request.POST

        filtered_data = []
        for src_idx in selected_global_ids:
            filtered_data.append(data[src_idx])

        json_path = os.path.join(settings.BASE_DIR, 'temp_llm_result.json')

        if use_preload and os.path.exists(json_path):
            json_path = os.path.join(settings.BASE_DIR, 'temp_llm_result_test.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            result = LLM_generate_for_extracted_data(filtered_data, configs)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        products = result
        #if result:
         #   for prod in result:
         #       resp = prod.get("response", {})
          #      products.append(resp)

        request.session['parsed_products'] = products

        return render(request, "process/parsing_result.html", {"products": products})

    return render(request, "process/parsing_result.html", {"products": []})

import re
from .models import Gas, ChemicalDesignation, Element, Powder, Metal
from django.shortcuts import redirect
from django.contrib import messages
import re

def save_selected_gases(request):
    if request.method != "POST":
        return redirect('iacpaas:llm_parsing')

    selected_indices = request.POST.getlist("selected_products")

    if not selected_indices:
        messages.error(request, "Не выбрано ни одного продукта.")
        return redirect('iacpaas:llm_parsing')

    products = request.session.get('parsed_products', [])

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
        product = product

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

            component, _ = Element.objects.get_or_create(formula=component_name)

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

from .models import Gas, Powder, MetalWire, Metal  # добавьте Metal в импорты


def material_list(request):
    available_types = []
    if Gas.objects.exists():
        available_types.append('gas')
    if Powder.objects.exists():  # исправлено: было PowderClass
        available_types.append('powder')
    if MetalWire.objects.exists():
        available_types.append('wire')
    if Metal.objects.exists():
        available_types.append('metal')

    selected_type = request.GET.get('type')
    if not selected_type or selected_type not in available_types:
        selected_type = available_types[0] if available_types else None

    context = {
        'selected_type': selected_type,
        'available_types': available_types,
        'gases': Gas.objects.all() if selected_type == 'gas' else Gas.objects.none(),
        'powders': Powder.objects.all() if selected_type == 'powder' else Powder.objects.none(),  # исправлено
        'wires': MetalWire.objects.all() if selected_type == 'wire' else MetalWire.objects.none(),
        'metals': Metal.objects.all() if selected_type == 'metal' else Metal.objects.none(),  # добавлено
    }
    return render(request, 'materials/material_list.html', context)

def gas_list(request):
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
from ..IACPaaS_api.gas_iasp import generate_gson_to_iacpaas_gase
from ..IACPaaS_api.wire_iasp import generate_gson_to_iacpaas_wires
from ..IACPaaS_api.powder_iasp import generate_json_to_iacpaas_powders
from ..IACPaaS_api.metal_iasp import generate_json_to_iacpaas_metal

from django.urls import reverse
from urllib.parse import urlencode

def send_to_iacpaas(request):
    if request.method != "POST":
        return redirect('iacpaas:gas_list')

    selected_wires_ids = request.POST.getlist('selected_wires')
    if selected_wires_ids:
        wires = MetalWire.objects.filter(id__in=selected_wires_ids)
        username = os.getenv('IACPAAS_USERNAME', acount_login)
        password = os.getenv('IACPAAS_PASSWORD', acount_password)
        api_key = signin(username, password)
        wires_json = generate_gson_to_iacpaas_wires(wires)
        result = import_resource(
            API_KEY=api_key,
            path=default_path,
            json=wires_json,
            clearIfExists=True
        )
        if result.get('success'):
            messages.success(request, f"Успешно отправлено {wires.count()} проволок в IACPaaS.")
        else:
            messages.error(request, f"Ошибка IACPaaS: {result.get('message', result)}")

        base_url = reverse('iacpaas:material_list')
        query_string = urlencode({'type': 'wire'})
        url = f'{base_url}?{query_string}'

        return redirect(url)

    selected_powders_ids = request.POST.getlist('selected_powders')
    if selected_powders_ids:
        powders = Powder.objects.filter(id__in=selected_powders_ids)
        username = os.getenv('IACPAAS_USERNAME', acount_login)
        password = os.getenv('IACPAAS_PASSWORD', acount_password)
        api_key = signin(username, password)
        powders_json = generate_json_to_iacpaas_powders(powders)
        result = import_resource(
            API_KEY=api_key,
            path=default_path,
            json=powders_json,
            clearIfExists=True
        )
        if result.get('success'):
            messages.success(request, f"Успешно отправлено {powders.count()} порошков в IACPaaS.")
        else:
            messages.error(request, f"Ошибка IACPaaS: {result.get('message', result)}")

        base_url = reverse('iacpaas:material_list')
        query_string = urlencode({'type': 'powder'})
        url = f'{base_url}?{query_string}'

        return redirect(url)

    selected_metals_ids = request.POST.getlist('selected_metals')
    if selected_metals_ids:
        metals = Metal.objects.filter(id__in=selected_metals_ids)
        username = os.getenv('IACPAAS_USERNAME', acount_login)
        password = os.getenv('IACPAAS_PASSWORD', acount_password)
        api_key = signin(username, password)
        metals_json = generate_json_to_iacpaas_metal(metals)
        result = import_resource(
            API_KEY=api_key,
            path=default_path,
            json=metals_json,
            clearIfExists=True
        )
        if result.get('success'):
            messages.success(request, f"Успешно отправлено {metals.count()} металлов в IACPaaS.")
        else:
            messages.error(request, f"Ошибка IACPaaS: {result.get('message', result)}")

        base_url = reverse('iacpaas:material_list')
        query_string = urlencode({'type': 'metal'})
        url = f'{base_url}?{query_string}'

        return redirect(url)


    selected_ids = request.POST.getlist('selected_gases')
    if not selected_ids:
        messages.warning(request, "Не выбрано ни одного газа для отправки.")
        return redirect('iacpaas:material_list')

    gases = Gas.objects.filter(id__in=selected_ids)
    if not gases.exists():
        messages.error(request, "Выбранные газы не найдены.")
        return redirect('iacpaas:material_list')

    try:
        username = os.getenv('IACPAAS_USERNAME', acount_login)
        password = os.getenv('IACPAAS_PASSWORD', acount_password)

        if not password:
            raise ValueError("Пароль IACPaaS не задан в переменных окружения")

        # Авторизация через connection.py
        api_key = signin(username, password)
        if not api_key:
            raise Exception("Не удалось получить токен доступа")

        # Сериализация
        gases_json = generate_gson_to_iacpaas_gase(gases)

        # Отправка через connection.py
        result = import_resource(
            API_KEY=api_key,
            path=default_path,
            json=gases_json,
            clearIfExists=True
        )

        print(result)

        if result.get('success'):
            messages.success(request, f"Успешно отправлено {gases.count()} газ(ов) в IACPaaS.")
        else:
            messages.error(request, f"Ошибка IACPaaS: {result.get('message', result)}")

    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")

    return redirect('iacpaas:material_list')


import os
import re
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

# Модели
from .models import (
    Gas,
    Element,
    ChemicalDesignation,
    PowderClass,
    MetalWire,
    PowderClass,
)
from django.apps import apps

from ..LLM.template_comparison import comparison_type_dic

import re

def extract_last_number(s):
    """
    Извлекает последнее число из строки и возвращает как float.
    Поддерживает целые и дробные числа (с точкой или запятой).
    """
    # Ищем все числа: возможны варианты 42, 3.14, 2,5
    numbers = re.findall(r'\d+(?:[.,]\d+)?', s)
    if numbers:
        # Заменяем запятую на точку для корректного преобразования
        return float(numbers[-1].replace(',', '.'))

    return 0

def generate_obj_dict(model, data_dict, item_data, base, main_obj):
    obj_data = {}
    for key, prop in data_dict.items():
        item_data[key] = item_data[key].replace('%', '').replace(',', '.')

        if "." in prop:
            prop = prop.split(".")
            prop_model = model._meta.get_field(prop[0]).related_model#apps.get_model('IACAPaaS_interactions', f'{prop[0]}')

            value = f'{item_data[key]}'

            field = model._meta.get_field(prop[0])
            if field.get_internal_type() == 'FloatField':
                value = extract_last_number(value)

            #value_without_digits = ''.join(char for char in str(item_data[key]) if not char.isdigit())

            if prop_model.__name__ == 'Element':
                value = Element.convert_to_subscript(item_data[key].strip())


            #print(value_without_digits)
            if type(value) == type("text"):
                model_param_without_digits = {f'{prop[1]}__iexact': value}
            else:
                model_param_without_digits = {f'{prop[1]}': value}

            try:
                element = prop_model.objects.filter(**model_param_without_digits).first()
                created = False
                if not element:
                    model_param_without_digits = {f'{prop[1]}': value}
                    element, created = prop_model.objects.get_or_create(**model_param_without_digits)
            except prop_model.DoesNotExist:

                model_param_with_digits = {f'{prop[1]}': value}

                element, created = prop_model.objects.get_or_create(**model_param_with_digits)
                print(element)

            obj_data[prop[0]] = element
        else:
            value = item_data[key]
            field = model._meta.get_field(prop)
            if field.get_internal_type() == 'FloatField':
                value = extract_last_number(value)

            obj_data[prop] = value

    if hasattr(model, base):
        obj_data[base] = main_obj

    return obj_data

def save_selected_products(request):
    if request.method != "POST":
        return redirect('iacpaas:llm_parsing')

    selected_indices = request.POST.getlist("selected_products")
    parsed_products = request.session.get('parsed_products', [])

    if not selected_indices or not parsed_products:
        messages.error(request, "Нет данных для сохранения.")
        return redirect('iacpaas:llm_parsing')

    saved_count = 0

    for idx_str in selected_indices:
        try:
            idx = int(idx_str)
            raw_item = parsed_products[idx]
        except (ValueError, IndexError, KeyError, TypeError):
            continue

        mat_type = raw_item.get("type")
        link = raw_item.get("link", "").strip()

        if not mat_type or not link:
            continue

        if mat_type == "gas_mixture":
            continue

        item = raw_item
        item["link"] = link
        item["type"] = mat_type

        comparison_type_dic[mat_type]

        first = True
        main_obj = None
        print(comparison_type_dic[mat_type])
        for key, data in comparison_type_dic[mat_type].items():
            model = apps.get_model('IACAPaaS_interactions', f'{key}')
            obj_data = {}

            item = raw_item
            print(item)
            for model_data in data:
                if type(data[model_data]) == dict:
                    data = data[model_data]
                    item = raw_item[model_data]
                break

            if first:
                model.objects.filter(
                    adress=raw_item['link'],
                ).delete()

            if type(item) == list:
                for it in item:
                    obj_data = {}
                    obj_data = generate_obj_dict(model, data, it, mat_type, main_obj)
                    obj = model.objects.create(**obj_data)
            else:
                obj_data = generate_obj_dict(model, data, item, mat_type, main_obj)
                obj = model.objects.create(**obj_data)

            if first:
                first = False
                main_obj = obj

        saved_count += 1


    messages.success(request, f"Успешно сохранено {saved_count} материалов.")
    request.session.pop('parsed_products', None)
    return redirect('iacpaas:material_list')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Gas, PowderClass, MetalWire

# Удаление газа
@require_http_methods(["POST"])
def delete_gas(request, pk):
    try:
        gas = Gas.objects.get(pk=pk)
        gas.delete()
        return JsonResponse({"success": True})
    except Gas.DoesNotExist:
        return JsonResponse({"success": False, "error": "Gas not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# Удаление порошка
@require_http_methods(["POST"])
def delete_powder(request, pk):
    try:
        powder = PowderClass.objects.get(pk=pk)
        powder.delete()
        return JsonResponse({"success": True})
    except PowderClass.DoesNotExist:
        return JsonResponse({"success": False, "error": "Powder not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# Удаление проволоки
@require_http_methods(["POST"])
def delete_wire(request, pk):
    try:
        wire = MetalWire.objects.get(pk=pk)
        wire.delete()
        return JsonResponse({"success": True})
    except MetalWire.DoesNotExist:
        return JsonResponse({"success": False, "error": "Wire not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@require_http_methods(["POST"])
def delete_metal(request, pk):
    try:
        metal = Metal.objects.get(pk=pk)
        metal.delete()
        return JsonResponse({"success": True})
    except Metal.DoesNotExist:
        return JsonResponse({"success": False, "error": "Metal not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)



from .element_fiiller import import_elements_from_json
from pathlib import Path
from ..IACPaaS_api.api_config import default_element_path_short, default_properties_path_short, default_terms_path_short, acount_login, acount_password
from ..IACPaaS_api.api_connection import signin, export_resource

def json_to_element(request):
    key = signin(acount_login, acount_password)
    elements = export_resource(key, default_element_path_short)

    elements = elements['data']
    import_elements_from_json(elements)

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/')

from .properties_filler import import_properties_from_json

def json_to_property(request):
    key = signin(acount_login, acount_password)

    elements = export_resource(key, default_properties_path_short)['data']

    print(elements)

    import_properties_from_json(json.loads(elements))

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/')


from .terms_filler import import_terms_from_json

def json_to_termin(request):
    key = signin(acount_login, acount_password)

    elements = export_resource(key, default_terms_path_short)['data']

    print(elements)

    import_terms_from_json(json.loads(elements))

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/')


from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Element


def elements_list(request):
    in_iacpaas_filter = request.GET.get('in_iacpaas')
    composite_filter = request.GET.get('composite')
    element_type_filter = request.GET.get('element_type')  # Новый фильтр
    search_query = request.GET.get('search', '').strip()

    elements = Element.objects.all()

    if in_iacpaas_filter == 'true':
        elements = elements.filter(in_iacpaas=True)
    elif in_iacpaas_filter == 'false':
        elements = elements.filter(in_iacpaas=False)

    if element_type_filter and element_type_filter in dict(Element.TYPE_CHOICES):
        elements = elements.filter(element_type=element_type_filter)

    if search_query:
        elements = elements.filter(
            Q(name__icontains=search_query) |
            Q(formula__icontains=search_query)
        )

    elements = elements.order_by('formula')
    paginator = Paginator(elements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'elements': page_obj,
        'element_type_choices': Element.TYPE_CHOICES,
    }
    return render(request, 'elements/element_list.html', context)


from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from .models import Property, PropertyType


def property_list(request):
    """Список свойств с фильтрацией и пагинацией"""
    queryset = Property.objects.all().select_related('type').order_by('name')

    in_iacpaas = request.GET.get('in_iacpaas')
    if in_iacpaas == 'true':
        queryset = queryset.filter(in_iacpaas=True)
    elif in_iacpaas == 'false':
        queryset = queryset.filter(in_iacpaas=False)

    type_id = request.GET.get('type')
    if type_id:
        queryset = queryset.filter(type_id=type_id)

    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(type__name__icontains=search)
        )

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')

    try:
        properties = paginator.page(page_number)
    except PageNotAnInteger:
        properties = paginator.page(1)
    except EmptyPage:
        properties = paginator.page(paginator.num_pages)

    property_types = PropertyType.objects.all().order_by('name')

    context = {
        'properties': properties,
        'property_types': property_types,
    }

    return render(request, 'properties/property_list.html', context)


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.db.models import Q
from .models import Termin, TerminType

def termin_list(request):
    """Список терминов с фильтрацией и пагинацией"""
    queryset = Termin.objects.all().select_related('termin_type').order_by('name')

    in_iacpaas = request.GET.get('in_iacpaas')
    if in_iacpaas == 'true':
        queryset = queryset.filter(in_iacpaas=True)
    elif in_iacpaas == 'false':
        queryset = queryset.filter(in_iacpaas=False)

    termin_type_id = request.GET.get('termin_type')
    if termin_type_id:
        queryset = queryset.filter(termin_type_id=termin_type_id)

    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(termin_type__name__icontains=search)
        )

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')

    try:
        termins = paginator.page(page_number)
    except PageNotAnInteger:
        termins = paginator.page(1)
    except EmptyPage:
        termins = paginator.page(paginator.num_pages)

    termin_types = TerminType.objects.all().order_by('name')

    context = {
        'termins': termins,
        'termin_types': termin_types,
    }

    return render(request, 'termins/termin_list.html', context)
