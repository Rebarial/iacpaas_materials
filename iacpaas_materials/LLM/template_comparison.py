powder_comparison = {
    "Powder": {
        "grade": "name",
        "base_material": "powder_class.name",
        "standards": ""
    },
    "PowderAnalog": {
      "analogs": {
          "name": "analog"
      }
    },
    "PowderPropertyValue": {
        "properties": {
            "property": "property.name",
            "value": "property_value"
        }
    },
    "Particle_form": {
        "powder_particle_shape": { ##Скорее всего другое название и тд надо доделать я только для газов сделал

        }
    }
}

gas_comparison = {
    "Gas" : {
        "name": "name",
        "formula": "formula",
        "grade": "grade",
        "brand": "brand",
        "standard": "standard",
        "link": "adress",
    },
    "ChemicalDesignation": {
        "chemical_designations": {
            "component_formula": "element.formula",
            "percent_value": "percent_value",
        }
    },

}

gas_mixture_comparison = {

}

metal_wire_comparison = {

}

metal_comparison = {

}


comparison_type_dic = {
    "powder": powder_comparison,
    "gas": gas_comparison,
    "gas_mixture": gas_mixture_comparison,
    "wire": metal_wire_comparison,
    "metal": metal_comparison,
}
