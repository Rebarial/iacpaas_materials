# utils.py
import json
from .models import Element


def import_elements_from_json(json_data):
    """
    Импорт элементов из JSON данных

    Args:
        json_data: dict или строка JSON

    Returns:
        dict: статистика импорта
    """
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    elements_data = data.get('successors', [])

    created_count = 0
    updated_count = 0

    for element_data in elements_data:
        element_name = element_data.get('name')

        # Извлекаем формулу
        formula = None
        for successor in element_data.get('successors', []):
            if successor.get('meta') == 'обозначение':
                formula = successor.get('value').strip()
                break

        if not formula or not element_name:
            continue

        obj, created = Element.objects.update_or_create(
            formula=formula,
            defaults={'name': element_name.strip(), 'in_iacpaas': True},
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        'created': created_count,
        'updated': updated_count,
        'total': created_count + updated_count
    }
