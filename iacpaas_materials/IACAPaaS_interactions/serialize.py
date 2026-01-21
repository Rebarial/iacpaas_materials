import json

def gases_to_iacpaas_dicts(gases):
    successors = []
    for gas in gases:
        gas_node = {
            "name": gas.name_gas,
            "property": [
                {"Химическое обозначение": gas.formula},
                {"Марка": gas.brand},
                {"Сорт": gas.grade},
                {"Стандарт": gas.standard},
            ],
            "adress": {"Источник": gas.adress_gas,
                       "Дата": gas.date_gas,
                       },
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

def powder_to_iacpaas_dicts(powders):
    successors = []
    for powder in powders:
        powder_node = {
            "class": powder.powder_type.name,
            "filling_method": powder.filling_method,
            "property": [
            ],
            "adress": {"Источник": powder.adress_pow,
                       "Дата": powder.date_pow,
                       },
            "components": [
            ]
        }
        successors.append(powder_node)

    return successors
