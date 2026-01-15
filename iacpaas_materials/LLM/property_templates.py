

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
    "powder_particle_shape": {
        "name": "",
        "size_value": "",
        "interval": "",
        # "interval_min": "",
        # "interval_max": "",
    },
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
            # "percent_min": "",
            # "percent_max": "",
            # "type": "",
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
