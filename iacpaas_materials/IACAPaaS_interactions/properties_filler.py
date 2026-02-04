import json
from .models import PropertyType, Property, PropertySynonym


def import_properties_from_json(data):
    """
    Импорт свойств материалов из JSON файла.
    Обрабатывает свойства, классы свойств и синонимы.
    """

    # Словарь для хранения найденных свойств при обходе дерева
    property_cache = {}

    def process_node(node, parent_property_type=None, parent_property=None):
        """Рекурсивная обработка узлов дерева"""
        node_type = node.get('type', '').strip()
        meta = node.get('meta', '').strip()
        name = node.get('name', '').strip()

        # 1. Класс свойств (НЕТЕРМИНАЛ с meta="Класс свойств")
        if meta == "Класс свойств" and name:
            property_type, _ = PropertyType.objects.get_or_create(
                name=name,
                defaults={'in_iacpaas': True}
            )
            if not property_type.in_iacpaas:
                property_type.in_iacpaas = True
                property_type.save()

            # Обработка дочерних узлов с передачей текущего класса
            for successor in node.get('successors', []):
                process_node(successor, parent_property_type=property_type)

        # 2. Свойство (НЕТЕРМИНАЛ с meta="Свойство")
        elif meta == "Свойство" and name and parent_property_type:
            property_obj, created = Property.objects.get_or_create(
                name=name,
                defaults={
                    'type': parent_property_type,
                    'in_iacpaas': True
                }
            )

            if not created:
                if property_obj.type != parent_property_type or not property_obj.in_iacpaas:
                    property_obj.type = parent_property_type
                    property_obj.in_iacpaas = True
                    property_obj.save()

            # Сохраняем в кэш для последующей обработки синонимов
            property_cache[id(node)] = property_obj

            # Рекурсивно обрабатываем потомков (включая синонимы)
            for successor in node.get('successors', []):
                process_node(successor, parent_property_type=parent_property_type, parent_property=property_obj)

        # 3. Синонимы (НЕТЕРМИНАЛ с meta="Синонимы")
        elif meta == "Синонимы" and parent_property:
            for synonym_node in node.get('successors', []):
                # Синоним — это ТЕРМИНАЛ-ЗНАЧЕНИЕ со строковым значением
                if synonym_node.get('type', '').strip() == "ТЕРМИНАЛ-ЗНАЧЕНИЕ" and \
                    synonym_node.get('valtype') == "STRING" and \
                    synonym_node.get('meta', '').strip() == "синоним":

                    synonym_value = synonym_node.get('value', '').strip()
                    if synonym_value:
                        PropertySynonym.objects.get_or_create(
                            name=synonym_value,
                            property=parent_property
                        )

        # 4. Прочие узлы — просто обходим рекурсивно
        else:
            for successor in node.get('successors', []):
                process_node(
                    successor,
                    parent_property_type=parent_property_type,
                    parent_property=parent_property
                )

    # Запуск обработки с корневого узла
    process_node(data)
