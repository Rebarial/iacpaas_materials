from django.urls import path
from ..LLM.views import llm_parsing
from .views import (
    choice_link,
    choice_materials,
    llm_parsing,
    save_selected_gases,
    gas_list,
    delete_gas,
    send_to_iacpaas,
    save_selected_products,
    material_list,
    delete_gas,
    delete_powder,
    delete_wire,
    json_to_element,
    elements_list,
    json_to_property,
    property_list,
)

app_name = "iacpaas"

urlpatterns = [

    #path("test/", llm_parsing, name="test"),

    path("choice_link/", choice_link, name="choice_link"),
    path("choice_materials/", choice_materials, name='choice_materials'),
    path("llm_parsing/", llm_parsing, name='llm_parsing'),
    path('save-gases/', save_selected_gases, name='save_selected_gases'),
    path('gases/', gas_list, name='gas_list'),
    path('gases/delete/<int:gas_id>/', delete_gas, name='delete_gas'),
    path('gases/send/', send_to_iacpaas, name='send_to_iacpaas'),

    path('save-products/', save_selected_products, name='save_selected_products'),
    path('materials/', material_list, name='material_list'),

    # urls.py
    path('delete-gas/<int:pk>/', delete_gas, name='delete_gas'),
    path('delete-powder/<int:pk>/', delete_powder, name='delete_powder'),
    path('delete-wire/<int:pk>/', delete_wire, name='delete_wire'),

    path('json_to_element/', json_to_element, name='json_to_element'),
    path('json_to_property/', json_to_property, name='json_to_property'),

    path('property_list/', property_list, name='properties_list'),
    path('elements_list/', elements_list, name='elements_list'),

]
