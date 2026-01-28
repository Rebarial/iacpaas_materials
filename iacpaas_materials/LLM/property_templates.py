

powder_template = {
    "name": "",
    "filling_method": "",
    "analogs": [
        {
            "name": "",
        },
    ],
    "properties": [
        {
            "property": "",
            "value": "",
        },
    ],
    "bulk_density": "",
    "flowability": "",
    "granulometric_composition": {
        "value": "",
        "d10": "",
        "d50": "",
        "d90": "",
        "average_value": "",
        "mass_fraction": "",
    },
    "powder_particle_shape": [
        {
            "shape": "",
            "obtaining_method": "",
            "size_value": "",
            "value_powder": "",
        },
    ],
    "powder_particle_sizes": [
        {
            "size_value": "",
            "application_method": "", # filling_method?
        },
    ],
}

gas_template = {
    "name": "",
    "formula": "",
    "grade": "",
    "brand": "",
    "standard": "",
    "chemical_designations": [
        {
            "component_formula": "",
            "designation_type": "",
            "percent_value": "",
        },
    ],
}
gas_mixture_template = {
    "name": "",
    "formula": "",
    "grade": "",
    "brand": "",
    "standard": "",
    "gas_composition": [
        {
            "gas": "",
            "concentration": "",
        },
    ],
}

metal_wire_template = {
    "name": "",
    "diameter": "",
    "interval_min": "",
    "analogs": [
        {
            "name": "",
        },
    ],
    "properties": [
        {
            "property": "",
            "value": "",
        },
    ],
    "elemental_composition": [
        {
            "element": "",
            "fraction": "",
        },
    ],
}

metal_template = {
    "name": "",
    "properties": [
        {
            "property": "",
            "value": "",
        },
    ],
    "elemental_composition": [
        {
            "element": "",
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
