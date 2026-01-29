from django.contrib import admin
from .models import Element, PropertyType, Property


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'formula', 'in_iacpaas')
    list_display_links = ('name',)
    search_fields = ('formula', 'name')
    ordering = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('formula', 'name')
        }),
    )

    class Meta:
        verbose_name = "Химический элемент"
        verbose_name_plural = "Химические элементы"


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'in_iacpaas', 'properties_count')
    list_display_links = ('name',)
    list_editable = ('in_iacpaas',)
    search_fields = ('name',)
    ordering = ('name',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'in_iacpaas')
        }),
    )

    @admin.display(description='Кол-во свойств')
    def properties_count(self, obj):
        return obj.property_set.count()


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_display', 'in_iacpaas')
    list_display_links = ('name',)
    list_editable = ('in_iacpaas',)
    list_filter = ('type', 'in_iacpaas')
    search_fields = ('name', 'type__name')
    ordering = ('name',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'type', 'in_iacpaas')
        }),
    )

    @admin.display(description='Класс свойства', ordering='type__name')
    def type_display(self, obj):
        return obj.type.name if obj.type else '-'
