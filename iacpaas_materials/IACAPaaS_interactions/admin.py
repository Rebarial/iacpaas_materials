from django.contrib import admin
from . import models


# Утилита для автоматического получения всех полей модели
def auto_fields(model):
    return [field.name for field in model._meta.fields if field.name != 'id']


# Утилита для регистрации модели с автоматическими настройками
def register_auto_admin(model_class):
    class AutoAdmin(admin.ModelAdmin):
        list_display = auto_fields(model_class)
        list_display_links = None  # По умолчанию можно кликать по любому полю для редактирования
        search_fields = [f.name for f in model_class._meta.fields if isinstance(f, (admin.CharField, admin.TextField))]
        list_filter = [f.name for f in model_class._meta.fields if
                       isinstance(f, (admin.BooleanField, admin.ForeignKey))]
        raw_id_fields = [f.name for f in model_class._meta.fields if isinstance(f, admin.ForeignKey)]

        # Разрешаем редактирование всех полей
        fields = auto_fields(model_class)

    admin.site.register(model_class, AutoAdmin)


# ===============
# Справочники
# ===============

@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.FillingMethod)
class FillingMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.FillingMethodOption)
class FillingMethodOptionAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.FillingMethodOption)
    list_filter = ('method', 'bool_fil')


@admin.register(models.PowderClass)
class PowderClassAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.PowderType)
class PowderTypeAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.PowderType)
    list_filter = ('powder_type', 'filling_method')


# ===============
# Порох
# ===============

@admin.register(models.PowderAnalog)
class PowderAnalogAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.PowderAnalog)
    raw_id_fields = ('powder', 'analog')


# ===============
# Свойства
# ===============

@admin.register(models.Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.PropertyValueType)
class PropertyValueTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.PropertySynonym)
class PropertySynonymAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.PropertySynonym)
    list_filter = ('property',)


@admin.register(models.PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.PropertyValue)
    list_filter = ('property', 'property_value', 'unit')
    raw_id_fields = ('property', 'property_value', 'unit')


@admin.register(models.PowderProperty)
class PowderPropertyAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.PowderProperty)
    raw_id_fields = ('powder', 'property_value')


# ===============
# Физические характеристики пороха
# ===============

@admin.register(models.BulkDensity)
class BulkDensityAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.BulkDensity)
    list_filter = ('unit',)
    raw_id_fields = ('powder', 'unit')


@admin.register(models.Flowability)
class FlowabilityAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.Flowability)
    list_filter = ('unit', 'bool_fil')
    raw_id_fields = ('powder', 'unit')


@admin.register(models.GranulometricComposition)
class GranulometricCompositionAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.GranulometricComposition)
    list_filter = ('unit',)
    raw_id_fields = ('powder', 'unit')


# ===============
# Форма частиц
# ===============

@admin.register(models.ParticleShape)
class ParticleShapeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.PowderParticleShape)
class PowderParticleShapeAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.PowderParticleShape)
    list_filter = ('shape', 'bool_par')
    raw_id_fields = ('powder', 'shape')


# ===============
# Газы и газовые смеси
# ===============

@admin.register(models.Gas)
class GasAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.Gas)
    search_fields = ('formula', 'grade', 'brand', 'standard')


@admin.register(models.ChemicalComponent)
class ChemicalComponentAdmin(admin.ModelAdmin):
    list_display = ('formula',)


@admin.register(models.ChemicalDesignationType)
class ChemicalDesignationTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.ChemicalDesignation)
class ChemicalDesignationAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.ChemicalDesignation)
    raw_id_fields = ('gas', 'component', 'designation_type')


@admin.register(models.GasMixture)
class GasMixtureAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.GasMixture)
    search_fields = ('formula', 'grade', 'brand', 'standard')


@admin.register(models.GasMixtureComponent)
class GasMixtureComponentAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.GasMixtureComponent)
    list_filter = ('unit',)
    raw_id_fields = ('mixture', 'gas', 'unit')


# ===============
# Металлическая проволока
# ===============

@admin.register(models.MetalWire)
class MetalWireAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.MetalWire)
    list_filter = ('diameter_unit',)
    raw_id_fields = ('diameter_unit',)


@admin.register(models.MetalWireProperty)
class MetalWirePropertyAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.MetalWireProperty)
    raw_id_fields = ('wire', 'property_value')


@admin.register(models.WireAnalog)
class WireAnalogAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.WireAnalog)
    raw_id_fields = ('wire', 'analog')


# ===============
# Элементный состав
# ===============

@admin.register(models.Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.ElementalComposition)
class ElementalCompositionAdmin(admin.ModelAdmin):
    list_display = auto_fields(models.ElementalComposition)
    list_filter = ('element',)
    raw_id_fields = ('wire', 'element')
