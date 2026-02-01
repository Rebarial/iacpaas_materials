# utils.py
import json
from .models import Element


#def import_elements_from_json(json_data):
import json
from .models import Element

def import_elements_from_json(json_data):
    """
    Парсит JSON из ИАСПААС и заполняет базу данных элементов

    :param json_data: JSON строка или словарь с данными
    :return: Кортеж (количество созданных, количество обновленных)
    """
    # Если передана строка, парсим в словарь
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    created_count = 0
    updated_count = 0

    # Начинаем обход с корневого элемента
    root = data

    # Обходим наследников корня (Химические элементы и Химические вещества)
    for successor in root.get('successors', []):
        name = successor.get('name', '').strip()

        if name == 'Химические элементы':
            c, u = _parse_chemical_elements(successor)
            created_count += c
            updated_count += u

        elif name == 'Химические вещества':
            c, u = _parse_chemical_substances(successor)
            created_count += c
            updated_count += u

    return created_count, updated_count

def _parse_chemical_elements(node):
    """Парсит химические элементы (атомы)"""
    created = 0
    updated = 0

    for element_node in node.get('successors', []):
        element_name = element_node.get('name', '').strip()
        symbol = None
        atomic_number = None

        # Извлекаем обозначение и порядковый номер
        for prop in element_node.get('successors', []):
            meta = prop.get('meta', '').strip()
            if meta == 'обозначение':
                symbol = prop.get('value', '').strip()
            elif meta == 'порядковый номер':
                atomic_number = prop.get('value')

        if symbol:
            # Создаем или обновляем элемент
            element, created_flag = Element.objects.update_or_create(
                formula=symbol,
                defaults={
                    'name': element_name,
                    'element_type': 'element',
                    'in_iacpaas': True
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

    return created, updated

def _parse_chemical_substances(node):
    """Парсит химические вещества (простые и сложные)"""
    created = 0
    updated = 0

    for category_node in node.get('successors', []):
        category_name = category_node.get('name', '').strip()

        # Определяем тип вещества
        if category_name == 'Простые вещества':
            substance_type = 'simple_substance'
        elif category_name == 'Сложные вещества':
            substance_type = 'complex_substance'
        else:
            continue

        # Парсим вещества в категории
        for substance_node in category_node.get('successors', []):
            substance_name = substance_node.get('name', '').strip()
            formula = None

            # Извлекаем формулу
            for prop in substance_node.get('successors', []):
                if prop.get('meta') == 'обозначение':
                    formula = prop.get('value', '').strip()
                    break

            if formula:
                # Создаем или обновляем вещество
                element, created_flag = Element.objects.update_or_create(
                    formula=formula,
                    defaults={
                        'name': substance_name,
                        'element_type': substance_type,
                        'in_iacpaas': True
                    }
                )

                if created_flag:
                    created += 1
                else:
                    updated += 1

    return created, updated

def convert_to_subscript(text):
    """
    Конвертирует цифры в нижний индекс (например, H2O -> H₂O)
    """
    subscript_map = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
    }

    result = ''
    for char in text:
        result += subscript_map.get(char, char)

    return result
