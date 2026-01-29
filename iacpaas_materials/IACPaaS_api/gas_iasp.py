from .api_config import default_path, default_element_path, ontology_path
import json

def generate_base():
    root = "Газы"
    type_successor = []

    template = {
        "title": f"{root}",
        "path": default_path,
        "json_type": "universal",
        "ontology": ontology_path['gas'],
        "name": f"{root}",
        "type": "КОРЕНЬ",
        "meta": f"{root}",
        "successors": [
            {
                "name": "Моногазы",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Моногазы",
                "successors": type_successor
            }
        ]
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
        "meta": "Класс газов",
        "successors": class_successor
    }

    type_successor.append(class_template)

    return class_template, class_successor

def generate_element(element):
    components_successor = []
    gas_name = element.name
    formula = element.formula
    grade = element.grade
    standard = element.standard
    adress = element.adress
    date = element.date
    components = element.chemicaldesignation_set.all()

    generate_components(components, components_successor)

    element_template = {
        "name": f"{gas_name}",
        "type": "НЕТЕРМИНАЛ",
        "meta": "Газ",
        "successors":
            [
                {
                    "value": f"{formula}",
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "Химическое обозначение",
                    #"original": "iagolnitckii.si@dvfu.ru / Мой Фонд / Загрузки / База химических элементов$/Гелий/He;"
                },
                {
                    "value": f"{grade}",
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "Марка"
                },
                {
                    "name": "Объемные доли компонентов",
                    "type": "НЕТЕРМИНАЛ",
                    "meta": "Объемные доли компонентов",
                    "successors": components_successor
                },
                {
                    "value": f"{standard}",
                    "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
                    "valtype": "STRING",
                    "meta": "Стандарт (норматив)",
                    "comment": "ТУ 20.11.11 - 005-45905715-2017 (НИИ КМ), ТУ 0271-135-31323949-2005 (Газпром)"
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
                                            "meta": "URL",
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
                }
            ]
    }

    return element_template

def generate_components(components: list, successor: list):
    index = 0

    for component in components:
        if not component.element.in_iacpaas:
            continue

        index += 1
        formula = component.element.formula
        value = component.percent_value

        if not value or value == "?":
            continue

        component_template = {
            "name": f"{index}",
            "type": "НЕТЕРМИНАЛ",
            "meta": "Компонент",
            "successors":
                [
                    {
                        "name": f"{formula}",
                        "type": "НЕТЕРМИНАЛ",
                        "meta": "Химическое обозначение",
                        "original": f"{default_element_path}/{component.element.name}/{component.element.formula};",
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

def generate_gson_to_iacpaas_gase(gases):

    base, type_successor = generate_base()

    for gase in gases:

        class_name = gase.name.split()[0]
        class_template, class_successor = get_or_create_class(type_successor, class_name)

        class_successor.append(generate_element(gase))


    return json.dumps(base)



