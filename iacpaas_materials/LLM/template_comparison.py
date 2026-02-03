powder_comparison = {
    "Powder": {
        "grade": "name",
        "base_material": "powder_class.name",
        "standards": "standards",
        "link": "adress"
    },
#    "PowderAnalog": {
 #       "analogs": {
  #          "name": "analog"
   #     }
   # },
    "PowderPropertyValue": {
        "properties": {
            "property": "property.name",
            "value": "property_value"
        }
    },
    "Particle_form": {
        "powder_particle_shape": { ##Скорее всего другое название и тд надо доделать я только для газов сделал
            "shape": "termin.name",
            "obtaining_method": "obtaining_method",
        }
    }
}

gas_comparison = {
    "Gas" : {
        "name": "name",
        "formula": "formula.formula",
        "mark_sort_or_grade": "grade",
        "brand": "brand",
        "standards": "standards",
        "link": "adress",
    },
    "ChemicalDesignation": {
        "chemical_composition": {
            "component_formula": "element.formula",
            "percent_value": "percent_value",
        }
    },

}

gas_mixture_comparison = {
    '''
    "GasMixture" : {
        "formula": "formula",
        "mark_sort_or_grade": "grade",
        "brand": "brand",
        "standards": "standards",
        "link": "adress",#  Нет поля в модели?
    },
    "GasMixtureComponent": {
        "gas_composition": {
            "gas": "gas.formula",
            "concentration": "concentration",
        }
    },
    '''
}

metal_wire_comparison = {
    "MetalWire" : {
        "base_material": "wire_class.name",
        "brand": "name",
        "standards": "standards",
        "link": "adress",
    },
    "MetalWire_diametrs": {
        "diameter_options": {
            "size_value": "value",
        }
    },
    "MetalWirePropertyValue": {
        "properties": {
            "property": "property.name",
            "value": "value",
        }
    },
 #   "WireAnalog": {
  #      "analogs": {
   #         "name": "analog.name",
    #    }
   # },
    "ElementalComposition_wire": {
        "elemental_composition": {
            "element": "element.formula",
            "fraction": "fraction",
        },
    },
}

metal_comparison = {
    "Metal" : {
        "metal_material": "metal_class.name",
        "brand": "name",
        "standards": "standards",
        "link": "adress",
    },
    "MetalPropertyValue": {
        "properties": {
            "property": "property.name",
            "value": "value",
        }
    },
    "ElementalComposition_metal": {
        "elemental_composition": {
            "element": "element.formula",
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
