import json
from copy import deepcopy

from .api_config import default_path, default_ontology_path_gase



class serialize_base:

    meta_types_template = {
        "Порошок": {
            "name": "",
            "type": "НЕТЕРМИНАЛ",
            "meta": "Металлический порошок",
            "successors": []
        },
        "Химическое обозначение": {
            "value": "",
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "STRING",
            "meta": "Химическое обозначение",
        },
        "Марка": {
            "value": "",
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "STRING",
            "meta": "Марка"
        },
        "Сорт": {
            "value": "",
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "STRING",
            "meta": "Сорт"
        },
        "Стандарт": {
            "value": "",
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "STRING",
            "meta": "Стандарт (норматив)",
        },
        "Доли": {
            "name": "Объемные доли компонентов",
            "type": "НЕТЕРМИНАЛ",
            "meta": "Объемные доли компонентов",
            "successors":
                []
        },
        "Компонент": {
            "name": "",
            "type": "НЕТЕРМИНАЛ",
            "meta": "Компонент",
            "successors":
                []
        },
        "Химическое обозначение компонент": {
            "name": "",
            "type": "НЕТЕРМИНАЛ",
            "meta": "Химическое обозначение",
            "successors": []
        },
        "%": {
            "value": "%",
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "STRING",
            "meta": "%"
        },
        "Не менее": {
            "name": "Не менее",
            "type": "НЕТЕРМИНАЛ",
            "meta": "Не менее",
            "successors": []
        },
        "≥": {
            "value": "≥",
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "STRING",
            "meta": "≥"
        },
        "Значение": {
            "value": 0,
            "type": "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype": "REAL",
            "meta": "Числовое значение"
        }
    }

    def _generate_template(self, root_type, ontology_path):
        self.__template = {
            "title": f"{root_type}",
            "path": default_path,
            "json_type": "universal",
            "ontology": ontology_path,
            "name": f"{root_type}",
            "type": "КОРЕНЬ",
            "meta": f"{root_type}",
            "successors": []
        }

    def _add_group_type(self, group_type):
        sucessors = []
        self.__template["successors"].append(
            {
                "name": f"{group_type}",
                "type": "НЕТЕРМИНАЛ",
                "meta": f"{group_type}",
                "successors": sucessors,
            }

        )
        return sucessors

    def _generate_class_name(self, el_name):
        return el_name.split()[0] if el_name.strip() else ""

    def __init__(self):
        pass

    def _add_property(self, element, property_to_add):

        meta = property_to_add["meta"]
        prop_value = property_to_add["value"]

        prop = deepcopy(self.meta_types_template[meta])

        if "value" in prop and not prop["value"]:
            prop["value"] = prop_value

        if "name" in prop and not prop["name"]:
            prop["name"] = prop_value

        element["successors"].append(prop)

        return prop

    def _add_adress(self, element, el_adress):

        adress_json =  \
        {
          "name" : "Источник",
          "type" : "НЕТЕРМИНАЛ",
          "meta" : "Источник",
          "successors" :
          [
          {
            "name" : "Тип",
            "type" : "НЕТЕРМИНАЛ",
            "meta" : "Тип",
            "successors" :
            [
            {
              "value" : "Интернет-сайт",
              "type" : "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
              "valtype" : "STRING",
              "meta" : "Интернет-сайт"
            }
            ]
          },
          {
            "name" : "Адрес",
            "type" : "НЕТЕРМИНАЛ",
            "meta" : "Адрес",
            "successors" :
            [
            {
              "value" : f"{el_adress['Источник']}",
              "type" : "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
              "valtype" : "STRING",
              "meta" : "URL",
            }
            ]
          },
          {
            "value" : f"{el_adress['Дата'].strftime('%d.%m.%Y-%H:%M:%S.%f')[:-3]}",
            "type" : "ТЕРМИНАЛ-ЗНАЧЕНИЕ",
            "valtype" : "DATE",
            "meta" : "Время загрузки"
          }
          ]
        }

        element["successors"].append(adress_json)

    def add_element(self, element_data):  # el_property, components, class_name=""):
        pass

    def add_elements(self, gases):
        for gase in gases:
            self.add_element(gase)

    def _add_components(self, element, components):
        pass

    def get_json(self):
        print(self.__template)
        return json.dumps(self.__template)
