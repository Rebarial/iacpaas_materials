import json

def gases_to_iacpaas_dicts(gases):
    successors = []
    for gas in gases:
        gas_node = {
            "el_name": gas.name_gas,
            "el_property": [
                {"Химическое обозначение": gas.formula},
                {"Марка": gas.brand},
                {"Сорт": gas.grade},
                 {"Стандарт": gas.standard},
            ],
            "components": [
                {
                    "formula": f"Компонент: {cd.component.formula}",
                        "value": str(cd.percent_value),
                }
                for cd in gas.chemicaldesignation_set.all()
            ]
        }
        successors.append(gas_node)

    return successors
