import json

def serialize_gases_to_iacpaas_json(gases, base_name="Экспорт газов"):
    successors = []
    for gas in gases:
        gas_node = {
            "name": gas.name_gas,
            "title": f"Газ: {gas.name_gas}",
            "type": "Газ",
            "properties": {
                "Формула": gas.formula,
                "Марка": gas.brand,
                "Степень чистоты": gas.grade,
                "Стандарт": gas.standard,
                "Источник": gas.adress_gas,
            },
            "successors": [
                {
                    "name": f"{cd.component.formula} ({cd.designation_type.name})",
                    "title": f"Компонент: {cd.component.formula}",
                    "type": "Химический компонент",
                    "properties": {
                        "Вещество": cd.component.formula,
                        "Тип обозначения": cd.designation_type.name,
                        "Содержание (%)": str(cd.percent_value),
                    },
                    "successors": []
                }
                for cd in gas.chemicaldesignation_set.all()
            ]
        }
        successors.append(gas_node)

    return json.dumps({
        "title": base_name,
        "name": base_name,
        "path": f"iagolnitckii.si@dvfu.ru / Мой Фонд / Газы / {base_name}",
        "json_type": "simple",
        "ontology": "iagolnitckii.si@dvfu.ru / Мой Фонд / Газы$;",
        "successors": successors
    }, ensure_ascii=False)
