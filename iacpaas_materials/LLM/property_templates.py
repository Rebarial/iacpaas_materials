

powder_template = {
    "full_name": "",
    "base_material": "",
    "grade": "",
    "standards": "",
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
            "size_range": "",
            "size_min": "",
            "size_max": "",
            "size_value_unit": "",
            "coating_application_method": "",
        },
    ],
    "properties": [
        {
            "property": "",
            "value": "",
            "property_type": "{Физическое/Механическое/...} свойство)",
        },
    ],
}

gas_template = {
    "full_name": "",
    "mark_sort_or_grade": "",
    "formula": "",
    "brand": "",
    "standards": "",
    "chemical_composition": [
        {
            "component_formula": "",
            "percent_value": "",
        },
    ],
}
gas_mixture_template = {
    "full_name": "",
    "mark_sort_or_grade": "",
    "formula": "",
    "brand": "",
    "standards": "",
    "gas_composition": [
        {
            "gas": "",
            "concentration": "",
        },
    ],
}

metal_wire_template = {
    "full_name": "",
    "brand": "",
    "base_material": "",
    "standards": "",
    "diameter_options": [
        {
            "size_value": "",
        },
    ],
    "analogs": [
        {
            "name": "",
        },
    ],
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
            "property_type": "",
        },
    ],
}

metal_template = {
    "full_name": "",
    "metal_material": "",
    "brand": "",
    "standards": "",
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
            "property_type": "",
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
