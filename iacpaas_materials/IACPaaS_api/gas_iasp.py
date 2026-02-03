from .api_config import default_path, default_element_path, ontology_path
import json
from ..IACAPaaS_interactions.models import Element


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
    formula = element.formula.formula
    grade = element.grade
    standard = element.standards
    adress = element.adress
    date = element.date
    components = element.chemicaldesignation_set.all()

    generate_components(components, components_successor)

    external_path = generate_external_path(element.formula)

    if element.formula.in_iacpaas:
        formula_path = {"original":  f"{default_element_path}/{external_path}{element.formula.name}/{element.formula.formula};"}
    else:
        formula_path = {}

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
                    **formula_path,
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
        if not component.element.in_iacpaas and not component.element.element_type == "compound_element":
            continue

        index += 1
        formula = component.element.formula
        value = component.percent_value

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
            print(component_template)
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
                            "meta": "Химическое обозначение",
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


def generate_gson_to_iacpaas_gase(gases):
    base, type_successor = generate_base()

    for gase in gases:
        class_name = gase.name.split()[0]
        class_template, class_successor = get_or_create_class(type_successor, class_name)

        class_successor.append(generate_element(gase))

    with open('test2.json', 'w', encoding='utf-8') as f:
        json.dump(base, f, ensure_ascii=False, indent=4)

    return json.dumps(base)
