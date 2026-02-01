from .api_config import default_path, default_element_path, ontology_path, default_properties_path
import json


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


def generate_properties(properies: list, successor: list):
    for property in properies:

        if not property.property.in_iacpaas or not property.value:
            continue

        successor.append(
            {
                "name": "Плотность вещества",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Свойство",
                "original": f"{default_properties_path}/{property.property.type.name}/{property.property.name};",
                "successors":
                    [
                        {
                            "name": "Не более",
                            "type": "НЕТЕРМИНАЛ",
                            "meta": "Не более",
                            "successors":
                                [
                                    {
                                        "value": "≤",
                                        "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                        "valtype": "STRING",
                                        "meta": "≤"
                                    },
                                    {
                                        "value": property.value,
                                        "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                                        "valtype": "REAL",
                                        "meta": "Числовое значение"
                                    }
                                ]
                        }
                    ]
            })


def generate_diametrs(diametrs: list, successor: list):
    successor.append({
        "value": "мм",
        "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
        "valtype": "STRING",
        "meta": "мм"
    })

    for diametr in diametrs:

        if not diametr:
            continue

        successor.append({
            "value": diametr.value,
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "REAL",
            "meta": "Числовое значение"
        })


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

        external_path = ""

        if component.element.element_type == "element":
            external_path = "Химические элементы/"
        elif component.element.element_type == "compound_element":
            external_path = "Химические элементы/"
        elif component.element.element_type == "simple_substance":
            external_path = "Химические вещества/Простые вещества/"
        elif component.element.element_type == "complex_substance":
            external_path = "Химические вещества/Сложные вещества/"

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

    return json.dumps(base)
