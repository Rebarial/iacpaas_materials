import json
from .models import PropertyType, Property


def import_properties_from_json(data):
    """
    Импорт свойств материалов из JSON файла.
    Обновляет связи свойств с классами при изменении.
    """

    def process_node(node, parent_property_type=None):
        """Рекурсивная обработка узлов дерева"""
        # Класс свойств
        if node.get('meta') == "Класс свойств":
            name = node.get('name', '').strip()
            if name:
                property_type, _ = PropertyType.objects.get_or_create(
                    name=name,
                    defaults={'in_iacpaas': True}
                )
                if not property_type.in_iacpaas:
                    property_type.in_iacpaas = True
                    property_type.save()

                # Обработка дочерних узлов
                for successor in node.get('successors', []):
                    process_node(successor, property_type)

        # Свойство
        elif node.get('meta') == "Свойство":
            name = node.get('name', '').strip()
            if name and parent_property_type:
                # Получаем или создаём свойство
                property_obj, created = Property.objects.get_or_create(
                    name=name,
                    defaults={
                        'type': parent_property_type,
                        'in_iacpaas': True
                    }
                )

                if not created:
                    # Обновляем только если изменился класс или флаг
                    if property_obj.type != parent_property_type or not property_obj.in_iacpaas:
                        property_obj.type = parent_property_type
                        property_obj.in_iacpaas = True
                        property_obj.save()

        # Прочие узлы — рекурсивно обходим потомков
        else:
            for successor in node.get('successors', []):
                process_node(successor, parent_property_type)

    # Запуск обработки
    process_node(data)
