from iacpaas_materials.iacpaas_materials.IACAPaaS_interactions.models import Powder

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
        "powder_particle_shape": { ##Скорее всего другое название и тд

        }
    }
}

gas_comparison = {

}

gas_mixture_comparison = {

}

metal_wire_comparison = {

}

metal_comparison = {

}


comparison_type = {
    "powder": powder_comparison,
    "gas": gas_comparison,
    "gas_mixture": gas_mixture_comparison,
    "wire": metal_wire_comparison,
    "metal": metal_comparison,
}
