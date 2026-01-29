powder_comparison = {
    "Powder": {
        "grade": "name",
        "base_material": "powder_class.name",
        "standards": "standards",
        "link": "adress"
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
            "shape": "name",
            "obtaining_method": "obtaining_method",
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
    "GasMixture" : {
        "formula": "formula",
        "grade": "grade",
        "brand": "brand",
        "standard": "standard",
        # "link": "adress",  Нет поля в модели?
    },
    "GasMixtureComponent": {
        "chemical_designations": {
            "component_formula": "gas.name",
            "percent_value": "concentration",
        }
    },
}

metal_wire_comparison = {
    "MetalWire" : {
        "name": "name",
        "wire_class": "wire_class.name",
        "link": "adress",
    },
    "MetalWire_diametrs": {
        "diameter_options": {
            "value": "value",
        }
    },
    "MetalWirePropertyValue": {
        "properties": {
            "property": "property.name",
            "value": "value",
        }
    },
    "WireAnalog": {
        "analogs": {
            "name": "analog.name",
        }
    },
    "ElementalComposition_wire": {
        "elemental_composition": {
            "element": "element.name",
            "fraction": "fraction",
        },
    },
}

metal_comparison = {
    "MetalWire" : {
        "metal_class": "metal_class.name",
        "name": "name",
        "standards": "adress",
        "link": "adress",
    },
    "MetalPropertyValue": {
        "properties": {
            "property": "property.name",
            "value": "value",
        }
    },
    "WireAnalog": {
        "analogs": {
            "name": "analog.name",
        }
    },
    "ElementalComposition_metal": {
        "elemental_composition": {
            "element": "element.name",
            "fraction": "fraction",
        },
    },
}


comparison_type_dic = {
    "powder": powder_comparison,
    "gas": gas_comparison,
    "gas_mixture": gas_mixture_comparison,
    "wire": metal_wire_comparison,
    "metal": metal_comparison,
}
