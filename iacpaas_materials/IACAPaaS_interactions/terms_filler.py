import json
from .models import TerminType, Termin


def import_terms_from_json(json_data):
    """
    Парсит JSON из ИАСПААС и заполняет базу данных терминов

    :param json_data: JSON строка или словарь с данными
    :return: Кортеж (количество созданных типов, количество созданных терминов)
    """
    # Если передана строка, парсим в словарь
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    created_types = 0
    created_terms = 0

    # Начинаем обход с корневого элемента
    root = data

    # Обходим наследников корня (разделы)
    for successor in root.get('successors', []):
        section_name = successor.get('name', '').strip()
        section_type = successor.get('type', '').strip()
        section_meta = successor.get('meta', '').strip()

        # Ищем разделы (типы терминов)
        if section_meta == 'Раздел':
            c_t, c_tr = _parse_section(successor)
            created_types += c_t
            created_terms += c_tr

    return created_types, created_terms


def _parse_section(node):
    """
    Парсит раздел (тип терминов) и все термины внутри него

    :param node: узел раздела
    :return: (количество созданных типов, количество созданных терминов)
    """
    section_name = node.get('name', '').strip()

    # Создаем тип термина (раздел)
    termin_type, type_created = TerminType.objects.get_or_create(
        name=section_name
    )

    created_types = 1 if type_created else 0
    created_terms = 0

    # Обходим наследников раздела (термины)
    for term_node in node.get('successors', []):
        term_name = term_node.get('name', '').strip()
        term_type = term_node.get('type', '').strip()
        term_meta = term_node.get('meta', '').strip()

        # Ищем термины
        if term_meta == 'Термин':
            # Создаем термин
            termin, term_created = Termin.objects.update_or_create(
                name=term_name,
                termin_type=termin_type,
                defaults={
                    'in_iacpaas': True
                }
            )

            if term_created:
                created_terms += 1

    return created_types, created_terms
