from django.urls import path
from ..LLM.views import llm_parsing

app_name = "iacpaas"

urlpatterns = [

    path("test/", llm_parsing, name="test"),

]
