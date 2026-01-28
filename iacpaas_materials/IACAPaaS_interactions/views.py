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

    max_pages = int(max_pages_raw) if max_pages_raw.strip().isdigit() else 50

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
                "product_links.json",
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
            with open(json_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            result = LLM_generate_for_extracted_data(filtered_data, configs)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        products = []
        if result:
            for prod in result:
                resp = prod.get("response", {})

                if resp.get("type") == "wire":
                    diameter = resp.get("diameter", "?")
                    interval_min = resp.get("interval_min", "?")
                    elements = [
                        comp.get("element")
                        for comp in resp.get("elemental_composition", [])
                        if comp.get("element")
                    ]
                    elements_str = ", ".join(elements) if elements else "не указан состав"
                    name = f"{diameter} – {interval_min}: {elements_str}"

                    new_resp = {"name": name}
                    for k, v in resp.items():
                        if k != "name":
                            new_resp[k] = v
                    resp = new_resp

                products.append(resp)


        request.session['parsed_products'] = products
        print(products)

        return render(request, "process/parsing_result.html", {"products": products})

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

def material_list(request):
    available_types = []
    if Gas.objects.exists():
        available_types.append('gas')
    if PowderClass.objects.exists():
        available_types.append('powder')
    if MetalWire.objects.exists():
        available_types.append('wire')

    selected_type = request.GET.get('type')

    if not selected_type or selected_type not in available_types:
        selected_type = available_types[0] if available_types else None

    context = {
        'selected_type': selected_type,
        'available_types': available_types,
        'gases': Gas.objects.all() if selected_type == 'gas' else Gas.objects.none(),
        'powders': PowderClass.objects.all() if selected_type == 'powder' else PowderClass.objects.none(),
        'wires': MetalWire.objects.all() if selected_type == 'wire' else MetalWire.objects.none(),
    }

    return render(request, 'materials/material_list.html', context)

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
    ChemicalComponent,
    ChemicalDesignationType,
    ChemicalDesignation,
    PowderClass,
    MetalWire,
    PowderClass,
)

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

        item = raw_item
        item["link"] = link
        item["type"] = mat_type

        if mat_type == "gas":
            name_gas_val = item.get("name", "").strip() or "Без названия"
            grade_val = item.get("grade", "").strip() or "N/A"
            brand_val = item.get("brand", "").strip() or "N/A"

            Gas.objects.filter(
                name_gas=name_gas_val,
                adress_gas=link,
                grade=grade_val,
                brand=brand_val
            ).delete()

            gas = Gas.objects.create(
                name_gas=name_gas_val,
                formula=item.get("formula", "").strip() or "N/A",
                grade=grade_val,
                brand=brand_val,
                standard=item.get("standard", "").strip() or "N/A",
                adress_gas=link,
            )

            for comp in item.get("chemical_designations", []):
                component_name = comp.get("component_formula", "").strip()
                designation_type_name = comp.get("designation_type", "").strip()
                percent_value = re.sub(r'[^0-9.,?]', '', comp.get("percent_value", "").strip().replace(",", "."))

                if component_name and designation_type_name:
                    component, _ = ChemicalComponent.objects.get_or_create(formula=component_name)
                    designation_type, _ = ChemicalDesignationType.objects.get_or_create(name=designation_type_name)
                    ChemicalDesignation.objects.create(
                        gas=gas,
                        component=component,
                        designation_type=designation_type,
                        percent_value=percent_value
                    )

            saved_count += 1

        elif mat_type == "powder":

            name_powder = item.get("name", "").strip()

            if not name_powder:
                name_powder = "Без названия"

            words = name_powder.split()

            if len(words) >= 2:

                powder_class_name = " ".join(words[:2])

            else:

                powder_class_name = name_powder

            method_name = item.get("filling_method", "Не указан").strip()

            link = raw_item.get("link", "").strip()

            if not link:
                continue

            powder_class, _ = PowderClass.objects.get_or_create(name=powder_class_name)

            PowderClass.objects.filter(adress_pow=link).delete()

            powder = PowderClass.objects.create(

                powder_type=powder_class,

                filling_method=option,

                adress_pow=link

            )

            for prop_data in item.get("properties", []):

                prop_name = prop_data.get("property", "").strip()

                prop_value_text = prop_data.get("value", "").strip()

                if not prop_name or not prop_value_text:
                    continue

                prop_obj, _ = Property.objects.get_or_create(name=prop_name)

                value_type, _ = PropertyValueType.objects.get_or_create(name="Текст")

                prop_val = PropertyValue.objects.create(

                    property=prop_obj,

                    property_value=value_type,

                    text_value=prop_value_text,

                    unit=None

                )

                PowderProperty.objects.create(

                    powder=powder,

                    property_value=prop_val

                )

            saved_count += 1

        elif mat_type == "wire":
            response_data = item
            diameter_str = item.get("diameter", "0").replace(" мм", "").strip()

            print(item)

            try:
                numbers = re.findall(r'[\d,\.]+', diameter_str.replace(',', '.'))
                diameters = [float(x) for x in numbers]
                diameter_min = min(diameters) if diameters else 0.0
                diameter_max = max(diameters) if len(diameters) > 1 else diameter_min
            except Exception:
                diameter_min = 0.0
                diameter_max = 0.0

            unit, _ = Unit.objects.get_or_create(name="мм")

            source_link = item.get("link", "").strip()

            MetalWire.objects.filter(adress_wire=source_link).delete()

            wire = MetalWire.objects.create(
                name_wire=response_data.get("name", "Неизвестно"),
                diameter_value=str(diameter_min),
                diameter_unit=unit,
                adress_wire=source_link
            )

            for prop_data in response_data.get("properties", []):
                prop_name = prop_data.get("property", "").strip()
                prop_value_text = prop_data.get("value", "").strip()
                if not prop_name or not prop_value_text:
                    continue

                prop_obj, _ = Property.objects.get_or_create(name=prop_name)
                value_type, _ = PropertyValueType.objects.get_or_create(name="Текст")
                prop_val_obj = PropertyValue.objects.create(
                    property=prop_obj,
                    property_value=value_type,
                    text_value=prop_value_text,
                    unit=None
                )
                MetalWireProperty.objects.create(
                    wire=wire,
                    property_value=prop_val_obj
                )

            for el_data in response_data.get("elemental_composition", []):
                el_name = el_data.get("element", "").strip()
                if el_name and el_name != "?":
                    element, _ = Element.objects.get_or_create(name=el_name)
                    ElementalComposition.objects.create(
                        wire=wire,
                        element=element,
                        fraction=-1
                    )

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
