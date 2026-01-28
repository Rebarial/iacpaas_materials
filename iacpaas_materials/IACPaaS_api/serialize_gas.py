import json
from copy import deepcopy

from .api_config import default_path, default_ontology_path_gase
from .serialize_base import serialize_base

class Gas_serialize(serialize_base):

    meta_types_template = {
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


    def _generate_class_name(self, el_name):
        return el_name.split()[0] if el_name.strip() else ""

    def __init__(self):
        root_type = "Газы"
        group_type = "Моногазы"
        self.__class_type = "Класс газов"
        self.__el_type = "Газ"

        self._generate_template(root_type, default_ontology_path_gase)

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
        class_name = ""
        el_name = element_data["name"]
        el_property = element_data["property"]
        components = element_data["components"]
        el_adress = element_data["adress"]

        if not class_name:
            class_name = self._generate_class_name(el_name)


        successors = self._add_group_type(self.__class_type)

        element = {
                "name": f"{class_name}",
                "type": "НЕТЕРМИНАЛ",
                "meta": f"{self.__class_type}",
                "successors": [
                    {
                        "name": f"{el_name}",
                        "type": "НЕТЕРМИНАЛ",
                        "meta": f"{self.__el_type}",
                        "successors":
                            []
                    }
                ]
            }

        successors.append(element)

        element = element["successors"][0]

        self._add_adress(element, el_adress)

        for prop in el_property:
            for key, value in prop.items():
                new_prop = {"meta": key, "value": str(value)}
                self._add_property(element, new_prop)

        self._add_components(element, components)


    def add_elements(self, gases):
        for gase in gases:
            self.add_element(gase)

    def _add_components(self, element, components):

        property_data = {"meta": "Доли", "value": ""}

        comp_successors = self._add_property(element, property_data)

        index = 0
        for comp in components:
            index += 1
            meta = "Компонент"

            property_data = {"meta": meta, "value": f"{index}"}

            sub_comp_successors = self._add_property(comp_successors, property_data)

            property_data = {"meta": "Химическое обозначение компонент", "value": f"{comp['formula']}"}

            chim_value = self._add_property(sub_comp_successors, property_data)

            chim_value["successors"] = []

            property_data = {"meta": "%", "value": ""}

            self._add_property(chim_value, property_data)

            property_data = {"meta": "Не менее", "value": ""}

            not_lower_successor = self._add_property(chim_value, property_data)

            property_data = {"meta": "≥", "value": ""}

            self._add_property(not_lower_successor, property_data)

            property_data = {"meta": "Значение", "value": comp["value"]}

            self._add_property(not_lower_successor, property_data)

    def get_json(self):
        print(self.__template)
        return json.dumps(self.__template)




