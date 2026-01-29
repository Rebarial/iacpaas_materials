

powder_template = {
    "base_material": "", # Добавить пример деления на base_material и grade
    "grade": "Марка",
    "standarts_list": "Стандарты (через запятую)",
    "analogs": [
        {
            "name": "",
        },
    ],
    # "bulk_density": "",
    # "flowability": "",
    # "granulometric_composition": {
    #     "value": "",
    #     "d10": "",
    #     "d50": "",
    #     "d90": "",
    #     "average_value": "",
    #     "mass_fraction": "",
    # },
    "powder_particle_shape": [
        {
            "shape": "",
            "obtaining_method": "",
        },
    ],
    "powder_particle_sizes": [ #Не нужно?
        {
            "size_value": "",
            "size_value_min": "",
            "size_value_max": "",
            "size_value_unit": "",
            "application_method": "",
        },
    ],
    "properties": [
        {
            "property": "",
            "value": "",
        },
    ],
}

gas_template = {
    "name": "", # Добавить пример деления на name и grade
    "grade": "",
    "formula": "Химическая формула (Например: H)",
    "brand": "",
    "standard": "Стандарты (через запятую)",
    "chemical_designations": [
        {
            "component_formula": "",
            # "designation_type": "",
            "percent_value": "",
        },
    ],
}
gas_mixture_template = {
    "name": "", # Добавить пример деления на name и grade
    "grade": "",
    "formula": "Химическая формула (Например: H2O)",
    "brand": "",
    "standard": "Стандарты (через запятую)",
    "gas_composition": [
        {
            "gas": "",
            "concentration": "",
        },
    ],
}

metal_wire_template = {
    "name": "", # Добавить пример деления на name и wire_class
    "wire_class": "",
    "diameter_options": [ ##!!!
        {
            "value": "",
        },
    ],
    "analogs": [
        {
            "name": "",
        },
    ],
    "material": "", #Можно найти сплав и его состав из уже спарженых?
    "elemental_composition": [
        {
            "element": "",
            "fraction": "",
        },
    ],
    "properties": [
        {
            "property": "",
            "value": "",
        },
    ],
}

metal_template = {
    "name": "", # Добавить пример деления на name и metal_class
    "metal_class": "",
    "standards": "Стандарты (через запятую)",
    "elemental_composition": [
        {
            "element": "",
            "fraction": "",
        },
    ],
    "properties": [
        {
            "property": "",
            "value": "",
        },
    ],
}


property_type_dic = {
    "powder": powder_template,
    "gas": gas_template,
    "gas_mixture": gas_mixture_template,
    "wire": metal_wire_template,
    "metal": metal_template,
}
