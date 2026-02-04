from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import *

# =========================
# Настройки для улучшения интерфейса
# =========================

class BaseAdmin(admin.ModelAdmin):
    """Базовый класс для общих настроек"""
    save_on_top = True
    list_per_page = 25


# =========================
# Элементный состав
# =========================

@admin.register(Element)
class ElementAdmin(BaseAdmin):
    list_display = ('formula', 'name', 'element_type', 'in_iacpaas')
    list_filter = ('element_type', 'in_iacpaas')
    search_fields = ('formula', 'name')
    list_editable = ('in_iacpaas',)
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('formula', 'name', 'element_type')
        }),
        (_('Дополнительные настройки'), {
            'fields': ('in_iacpaas',)
        }),
    )


@admin.register(PropertyType)
class PropertyTypeAdmin(BaseAdmin):
    list_display = ('name', 'in_iacpaas')
    list_filter = ('in_iacpaas',)
    search_fields = ('name',)
    list_editable = ('in_iacpaas',)


@admin.register(Property)
class PropertyAdmin(BaseAdmin):
    list_display = ('name', 'type', 'in_iacpaas')
    list_filter = ('type', 'in_iacpaas')
    search_fields = ('name',)
    list_editable = ('in_iacpaas',)


# =========================
# Порошки - Основная модель с встроенными редакторами
# =========================

class ElementalCompositionPowderInline(admin.TabularInline):
    model = ElementalComposition_powder
    extra = 0
    min_num = 0
    fields = ('element', 'fraction')
    autocomplete_fields = ('element',)
    verbose_name = _('Элемент состава')
    verbose_name_plural = _('Элементный состав')


class ParticleFormInline(admin.TabularInline):
    model = Particle_form
    extra = 1
    fields = ('termin', 'obtaining_method')
    verbose_name = _('termin')
    verbose_name_plural = _('termin')


class PowderAnalogInline(admin.TabularInline):
    model = PowderAnalog
    fk_name = 'powder'
    extra = 1
    fields = ('analog',)
    autocomplete_fields = ('analog',)
    verbose_name = _('Аналог')
    verbose_name_plural = _('Аналоги')


class PowderPropertyValueInline(admin.TabularInline):
    model = PowderPropertyValue
    extra = 1
    fields = ('property', 'property_value', 'unit')
    autocomplete_fields = ('property',)
    verbose_name = _('Свойство')
    verbose_name_plural = _('Свойства')


@admin.register(PowderClass)
class PowderClassAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_name = _('Класс порошка')
    verbose_name_plural = _('Классы порошков')


@admin.register(Powder)
class PowderAdmin(BaseAdmin):
    list_display = ('name', 'powder_class', 'adress', 'date', 'standards')
    list_filter = ('powder_class', 'date')
    search_fields = ('name', 'standards', 'adress')
    date_hierarchy = 'date'
    inlines = [
        ElementalCompositionPowderInline,
        ParticleFormInline,
        PowderAnalogInline,
        PowderPropertyValueInline,
    ]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('powder_class', 'name', 'adress', 'standards')
        }),
        (_('Дополнительная информация'), {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date',)
    verbose_name = _('Порошок')
    verbose_name_plural = _('Порошки')


# =========================
# Газы и газовые смеси
# =========================

class ChemicalDesignationInline(admin.TabularInline):
    model = ChemicalDesignation
    extra = 0
    min_num = 0
    fields = ('element', 'percent_value')
    autocomplete_fields = ('element',)
    verbose_name = _('Компонент')
    verbose_name_plural = _('Химический состав')


@admin.register(Gas)
class GasAdmin(BaseAdmin):
    list_display = ('name', 'formula', 'grade', 'brand', 'date')
    list_filter = ('brand', 'grade', 'date')
    search_fields = ('name', 'formula', 'brand', 'standards')
    date_hierarchy = 'date'
    inlines = [ChemicalDesignationInline]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'formula', 'grade', 'brand')
        }),
        (_('Документация'), {
            'fields': ('standards', 'adress')
        }),
        (_('Дополнительная информация'), {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date',)
    verbose_name = _('Газ')
    verbose_name_plural = _('Газы')


class GasMixtureComponentInline(admin.TabularInline):
    model = GasMixtureComponent
    extra = 0
    min_num = 0
    fields = ('gas', 'concentration')
    autocomplete_fields = ('gas',)
    verbose_name = _('Компонент')
    verbose_name_plural = _('Компоненты смеси')


@admin.register(GasMixture)
class GasMixtureAdmin(BaseAdmin):
    list_display = ('formula', 'grade', 'brand', 'standards')
    list_filter = ('brand', 'grade')
    search_fields = ('formula', 'brand', 'standards')
    inlines = [GasMixtureComponentInline]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('formula', 'grade', 'brand')
        }),
        (_('Документация'), {
            'fields': ('standards', 'adress')
        }),
    )
    verbose_name = _('Газовая смесь')
    verbose_name_plural = _('Газовые смеси')


# =========================
# Металлическая проволока
# =========================

class MetalWireDiametrsInline(admin.TabularInline):
    model = MetalWire_diametrs
    extra = 0
    min_num = 0
    fields = ('value',)
    verbose_name = _('Диаметр')
    verbose_name_plural = _('Диаметры')


class MetalWirePropertyValueInline(admin.TabularInline):
    model = MetalWirePropertyValue
    extra = 1
    fields = ('property', 'value', 'unit')
    autocomplete_fields = ('property',)
    verbose_name = _('Свойство')
    verbose_name_plural = _('Свойства')


class WireAnalogInline(admin.TabularInline):
    model = WireAnalog
    fk_name = 'wire'
    extra = 1
    fields = ('analog',)
    autocomplete_fields = ('analog',)
    verbose_name = _('Аналог')
    verbose_name_plural = _('Аналоги')


class ElementalCompositionWireInline(admin.TabularInline):
    model = ElementalComposition_wire
    extra = 0
    min_num = 0
    fields = ('element', 'fraction')
    autocomplete_fields = ('element',)
    verbose_name = _('Элемент состава')
    verbose_name_plural = _('Элементный состав')


@admin.register(MetalWireClass)
class MetalWireClassAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_name = _('Класс проволки')
    verbose_name_plural = _('Классы проволки')


@admin.register(MetalWire)
class MetalWireAdmin(BaseAdmin):
    list_display = ('name', 'wire_class', 'adress', 'date')
    list_filter = ('wire_class', 'date')
    search_fields = ('name', 'standards', 'adress')
    date_hierarchy = 'date'
    inlines = [
        MetalWireDiametrsInline,
        MetalWirePropertyValueInline,
        WireAnalogInline,
        ElementalCompositionWireInline,
    ]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('name', 'wire_class', 'adress', 'standards')
        }),
        (_('Дополнительная информация'), {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date',)
    verbose_name = _('Металлическая проволока')
    verbose_name_plural = _('Металлическая проволока')


# =========================
# Металлы и сплавы
# =========================

class MetalPropertyValueInline(admin.TabularInline):
    model = MetalPropertyValue
    extra = 1
    fields = ('property', 'value', 'unit')
    autocomplete_fields = ('property',)
    verbose_name = _('Свойство')
    verbose_name_plural = _('Свойства')


class ElementalCompositionMetalInline(admin.TabularInline):
    model = ElementalComposition_metal
    extra = 0
    min_num = 0
    fields = ('element', 'fraction')
    autocomplete_fields = ('element',)
    verbose_name = _('Элемент состава')
    verbose_name_plural = _('Элементный состав')


@admin.register(MetalClass)
class MetalClassAdmin(BaseAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    verbose_name = _('Класс сплава')
    verbose_name_plural = _('Классы сплавов')


@admin.register(Metal)
class MetalAdmin(BaseAdmin):
    list_display = ('name', 'metal_class', 'adress', 'date')
    list_filter = ('metal_class', 'date')
    search_fields = ('name', 'standards', 'adress')
    date_hierarchy = 'date'
    inlines = [
        MetalPropertyValueInline,
        ElementalCompositionMetalInline,
    ]
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('metal_class', 'name', 'adress', 'standards')
        }),
        (_('Дополнительная информация'), {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date',)
    verbose_name = _('Металл')
    verbose_name_plural = _('Металлы')


# =========================
# Регистрация связанных моделей (без отдельных админок)
# =========================

# Эти модели уже доступны через встроенные редакторы в основных моделях,
# но для полноты регистрируем их с базовыми настройками

@admin.register(ElementalComposition_powder)
class ElementalCompositionPowderAdmin(BaseAdmin):
    list_display = ('powder', 'element', 'fraction')
    list_filter = ('powder', 'element')
    search_fields = ('powder__name', 'element__formula')


@admin.register(Particle_form)
class ParticleFormAdmin(BaseAdmin):
    list_display = ('powder', 'termin', 'obtaining_method')
    list_filter = ('powder',)
    search_fields = ('termin', 'obtaining_method')


@admin.register(PowderAnalog)
class PowderAnalogAdmin(BaseAdmin):
    list_display = ('powder', 'analog')
    search_fields = ('powder__name', 'analog__name')


@admin.register(PowderPropertyValue)
class PowderPropertyValueAdmin(BaseAdmin):
    list_display = ('powder', 'property', 'property_value', 'unit')
    list_filter = ('property',)
    search_fields = ('powder__name',)


@admin.register(ChemicalDesignation)
class ChemicalDesignationAdmin(BaseAdmin):
    list_display = ('gas', 'element', 'percent_value')
    list_filter = ('gas', 'element')
    search_fields = ('gas__name', 'element__formula')


@admin.register(GasMixtureComponent)
class GasMixtureComponentAdmin(BaseAdmin):
    list_display = ('mixture', 'gas', 'concentration')
    list_filter = ('mixture', 'gas')
    search_fields = ('mixture__formula', 'gas__name')


@admin.register(MetalWire_diametrs)
class MetalWireDiametrsAdmin(BaseAdmin):
    list_display = ('wire', 'value')
    list_filter = ('wire',)
    search_fields = ('wire__name',)


@admin.register(MetalWirePropertyValue)
class MetalWirePropertyValueAdmin(BaseAdmin):
    list_display = ('wire', 'property', 'value', 'unit')
    list_filter = ('property',)
    search_fields = ('wire__name',)


@admin.register(WireAnalog)
class WireAnalogAdmin(BaseAdmin):
    list_display = ('wire', 'analog')
    search_fields = ('wire__name', 'analog__name')


@admin.register(ElementalComposition_wire)
class ElementalCompositionWireAdmin(BaseAdmin):
    list_display = ('wire', 'element', 'fraction')
    list_filter = ('wire', 'element')
    search_fields = ('wire__name', 'element__formula')


@admin.register(MetalPropertyValue)
class MetalPropertyValueAdmin(BaseAdmin):
    list_display = ('metal', 'property', 'value', 'unit')
    list_filter = ('property',)
    search_fields = ('metal__name',)


@admin.register(ElementalComposition_metal)
class ElementalCompositionMetalAdmin(BaseAdmin):
    list_display = ('metal', 'element', 'fraction')
    list_filter = ('metal', 'element')
    search_fields = ('metal__name', 'element__formula')


@admin.register(PropertySynonym)
class PropertySynonymAdmin(admin.ModelAdmin):
    """Отдельная админка для синонимов"""
    list_display = ('name', 'property', 'property_type')
    list_filter = ('property__type',)
    search_fields = ('name', 'property__name', 'property__type__name')
    raw_id_fields = ('property',)  # Удобный поиск для свойства

    def property_type(self, obj):
        """Отображение типа свойства"""
        return obj.property.type if obj.property else None

    property_type.short_description = 'Класс свойства'
    property_type.admin_order_field = 'property__type__name'
