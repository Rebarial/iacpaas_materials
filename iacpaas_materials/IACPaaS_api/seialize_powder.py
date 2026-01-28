from .serialize_base import serialize_base
import json
from copy import deepcopy
from .api_config import default_path, default_ontology_path_powder

class Gas_serialize(serialize_base):

    def _generate_class_name(self, el_name):
        return el_name.split()[0] if el_name.strip() else ""

    def __init__(self):
        root_type = "Порошки"
        self._generate_template(root_type, default_ontology_path_powder)

    def add_element(self, element_data, element_class):

        el_name = element_data["name"]

        el = self._add_property(element_class, {
            "meta": "Порошок",
            "name": f"{el_name}"
        })


        pass


    def add_elements(self, elements):
        for element_type, element_data in elements.items():
            element_type_data = {
                "name": f"{element_type}",
                "type": "НЕТЕРМИНАЛ",
                "meta": "Класс металлических порошков",
                "successors":
                    []
            }
            self.__template["successors"].append(element_type_data)
            for element in element_data:
                self.add_element(element_data, element_type_data)

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




