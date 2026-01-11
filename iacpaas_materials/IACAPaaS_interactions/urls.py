from django.urls import path
from ..LLM.views import llm_parsing
from .views import choice_link, choice_materials, llm_parsing

app_name = "iacpaas"

urlpatterns = [

    #path("test/", llm_parsing, name="test"),

    path("choice_link/", choice_link, name="choice_link"),
    path("choice_materials/", choice_materials, name='choice_materials'),
    path("llm_parsing/", llm_parsing, name='llm_parsing'),

]
