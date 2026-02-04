from .api_config import default_path, default_element_path, ontology_path, default_properties_path
import json
from ..IACAPaaS_interactions.models import Element


def generate_base():
    root = "Металлопроволочные материалы"
    type_successor = []

    template = {
        "title": f"{root}",
        "path": default_path,
        "json_type": "universal",
        "ontology": ontology_path['wire'],
        "name": f"{root}",
        "type": "КОРЕНЬ",
        "meta": f"{root}",
        "successors": type_successor
    }

    return template, type_successor


def get_or_create_class(type_successor, class_name):
    for class_temp in type_successor:
        if class_temp["name"] == class_name:
            return class_temp, class_temp["successors"]

    class_successor = []

    class_template = {
        "name": f"{class_name}",
        "type": "НЕТЕРМИНАЛ",
        "meta": "Класс металлических проволок",
        "successors": class_successor
    }

    type_successor.append(class_template)

    return class_template, class_successor


def generate_element(element):
    components_successor = []
    diametrs_successor = []
    property_successor = []
    name = element.name
    standard = element.standards
    adress = element.adress
    date = element.date
    components = element.elementalcomposition_wire_set.all()
    diametrs = element.metalwire_diametrs_set.all()
    properties = element.metalwirepropertyvalue_set.all()

    generate_components(components, components_successor)
    generate_diametrs(diametrs, diametrs_successor)
    generate_properties(properties, property_successor)

    element_template = {
        "name": f"{name}",
        "type": "НЕТЕРМИНАЛ",
        "meta": "Металлическая проволока",
        "successors":
            [
                {
                    "name": "Аналоги",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Аналоги",
                    "successors": [],
                },
                {
                    "name": "Элементный состав",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Элементный состав",
                    "successors": components_successor,

                },
                {
                    "name": "Диаметр",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Диаметр",
                    "successors": diametrs_successor,
                },
                {
                    "name": "Источник",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Источник",
                    "successors":
                        [
                            {
                                "name": "Тип",
                                "type": "НЕТЕРМИНАЛ",
                                "meta": "Тип",
                                "successors":
                                    [
                                        {
                                            "value": "Интернет-сайт",
                                            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                            "valtype": "STRING",
                                            "meta": "Интернет-сайт"
                                        }
                                    ]
                            },
                            {
                                "name": "Адрес",
                                "type": "НЕТЕРМИНАЛ",
                                "meta": "Адрес",
                                "successors":
                                    [
                                        {
                                            "value": f"{adress}",
                                            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                            "valtype": "STRING",
                                            "meta": "URL"
                                        }
                                    ]
                            },
                            {
                                "value": f"{date.strftime('%d.%m.%Y-%H:%M:%S.%f')[:-3]}",
                                "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                "valtype": "DATE",
                                "meta": "Время загрузки"
                            }
                        ]
                },
                {
                    "name": "Свойства",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Свойства",
                    "successors": property_successor,
                },
                {
                    "value": f"{standard}",
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "Стандарт (норматив)"
                }
            ]
    }

    return element_template


from collections import defaultdict

def get_canonical_property(property_obj):
    """Возвращает оригинальное свойство, если оно есть, иначе само свойство"""
    return property_obj.original if property_obj.original else property_obj

def generate_properties(properties: list, successor: list):
    """
    Генерирует структуру свойств с интервалами для классов с несколькими значениями.

    Для классов свойств с >=2 записями формирует интервал "От ... до ..."
    через два блока: "Не менее" (≥ мин) и "Не более" (≤ макс).
    Для классов с 1 записью — стандартный блок "Не более".
    """
    # Шаг 1: Фильтрация валидных свойств
    valid_items = [
        p for p in properties
        if get_canonical_property(p.property).in_iacpaas
        and p.value is not None
        and p.value != 0.0
    ]

    # Шаг 2: Группировка по типу свойства (используем ID для эффективности)
    groups = defaultdict(list)
    for item in valid_items:
        type_id = get_canonical_property(item.property).type_id if get_canonical_property(item.property).type else None
        groups[type_id].append(item)

    # Шаг 3: Обработка каждой группы
    for type_id, items in groups.items():
        if not items:
            continue

        # Получаем имя класса и свойства из первого элемента группы
        first_item = items[0]
        canonical_property = get_canonical_property(first_item.property)

        property_type_name = canonical_property.type.name if canonical_property.type else "Без класса"
        property_name = canonical_property.name

        original_path = f"{default_properties_path}/{property_type_name}/{property_name};"

        if len(items) == 1:
            item = items[0]
            value_successor = []

            value_successor.append(
                {
                    "value": "≤",
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "≤"
                }
            )

            value_successor.append(
                {
                    "value": item.value,
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "REAL",
                    "meta": "Числовое значение"
                },
            )

            if (items[0].unit and items[0].unit != "-" and items[0].unit != ""):
                value_successor.append({
                    "value": items[0].unit,
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "единица измерения",
                }
                )

            successor.append({
                "name": property_name,
                "type": "НЕТЕРМИНАЛ",
                "meta": "Свойство",
                "original": original_path,
                "successors": [
                    {
                        "name": "Не более",
                        "type": "НЕТЕРМИНАЛ",
                        "meta": "Не более",
                        "successors": value_successor
                    }
                ]
            })
        else:
            values = [item.value for item in items]
            min_val = min(values)
            max_val = max(values)

            value_successor = []

            value_successor.append({
                "name": "Нижняя граница",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Нижняя граница",
                "successors":
                    [
                        {
                            "value": min_val,
                            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                            "valtype": "REAL",
                            "meta": "Числовое значение"
                        }
                    ]
            })

            value_successor.append({
                "name": "Верхняя граница",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Верхняя граница",
                "successors":
                    [
                        {
                            "value": max_val,
                            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                            "valtype": "REAL",
                            "meta": "Числовое значение"
                        }
                    ]
            })

            if (items[0].unit and items[0].unit != "-" and items[0].unit != ""):
                value_successor.append(
                    {
                        "value": items[0].unit,
                        "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                        "valtype": "STRING",
                        "meta": "единица измерения",
                    })

            successor.append({
                "name": property_type_name,
                "type": "НЕТЕРМИНАЛ",
                "meta": "Свойство",
                "original": original_path,
                "successors": [
                    {
                        "name": f"Числовой интервал",
                        "type": "НЕТЕРМИНАЛ",
                        "meta": "Числовой интервал",
                        "successors": value_successor
                    }]}
            )


def generate_diametrs(diametrs: list, successor: list):
    successor.append({
        "value": "мм",
        "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
        "valtype": "STRING",
        "meta": "мм"
    })

    seen_values = set()

    for diametr in diametrs:
        if not diametr:
            continue

        value = diametr.value
        if value is None or value in seen_values:
            continue

        seen_values.add(value)
        successor.append({
            "value": value,
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "REAL",
            "meta": "Числовое значение"
        })


def generate_external_path(element):
    external_path = ""

    if element.element_type == "element":
        external_path = "Химические элементы/"
    elif element.element_type == "simple_substance":
        external_path = "Химические вещества/Простые вещества/"
    elif element.element_type == "complex_substance":
        external_path = "Химические вещества/Сложные вещества/"

    return external_path


def generate_components(components: list, successor: list):
    index = 0

    for component in components:
        if not component.element.in_iacpaas:
            continue

        index += 1
        formula = component.element.formula
        value = component.fraction

        if not value or value == "?":
            continue

        external_path = generate_external_path(component.element)

        if component.element.element_type == "compound_element":

            complex_successors = []

            complex_successors.append(
                {
                    "name": "Содержание",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Содержание",
                    "successors":
                        [
                            {
                                "value": "%",
                                "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                "valtype": "STRING",
                                "meta": "%"
                            },
                            {
                                "name": "Не менее",
                                "type": "НЕТЕРМИНАЛ",
                                "meta": "Не менее",
                                "successors":
                                    [
                                        {
                                            "value": "≥",
                                            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                            "valtype": "STRING",
                                            "meta": "≥"
                                        },
                                        {
                                            "value": value,
                                            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                            "valtype": "REAL",
                                            "meta": "Числовое значение"
                                        }
                                    ]
                            }
                        ]
                }
            )

            formulas = [part.strip() for part in component.element.formula.strip().split("+")]
            print(formulas)

            for formula in formulas:
                try:
                    el_split = Element.objects.get(formula=formula)
                    if not el_split.in_iacpaas:
                        continue
                except:
                    continue

                external_path = generate_external_path(el_split)

                complex_successors.append({
                    "value": f"{el_split.formula}",
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "Химическое обозначение",
                    "original": f"{default_element_path}/{external_path}{el_split.name}/{el_split.formula};"
                },
                )

            component_template = {
                "name": f"{index}",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Компонент",
                "successors":
                    [
                        {
                            "name": "Совокупность химических веществ",
                            "type": "НЕТЕРМИНАЛ",
                            "meta": "Совокупность химических веществ",
                            "successors": complex_successors
                        }
                    ]
            }

        else:
            component_template = {
                "name": f"{index}",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Компонент",
                "successors":
                    [
                        {
                            "name": f"{formula}",
                            "type": "НЕТЕРМИНАЛ",
                            "meta": "Химический элемент",
                            "original": f"{default_element_path}/{external_path}{component.element.name}/{component.element.formula};",
                            "successors":
                                [
                                    {
                                        "value": "%",
                                        "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                        "valtype": "STRING",
                                        "meta": "%"
                                    },
                                    {
                                        "name": "Не менее",
                                        "type": "НЕТЕРМИНАЛ",
                                        "meta": "Не менее",
                                        "successors":
                                            [
                                                {
                                                    "value": "≥",
                                                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                                    "valtype": "STRING",
                                                    "meta": "≥"
                                                },
                                                {
                                                    "value": value,
                                                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                                    "valtype": "REAL",
                                                    "meta": "Числовое значение"
                                                }
                                            ]
                                    }
                                ]
                        }
                    ]
            }

        successor.append(component_template)


def generate_gson_to_iacpaas_wires(wires):
    base, type_successor = generate_base()

    for wire in wires:
        class_name = wire.wire_class.name
        class_template, class_successor = get_or_create_class(type_successor, class_name)

        class_successor.append(generate_element(wire))

    with open('test2.json', 'w', encoding='utf-8') as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

    return json.dumps(base)
