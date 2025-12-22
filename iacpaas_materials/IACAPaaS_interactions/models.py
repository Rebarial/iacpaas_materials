from django.db import models

# =========================
# Справочники
# =========================

class Unit(models.Model):
    class Meta:
        db_table = "Единицы_измерения"
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FillingMethod(models.Model):
    class Meta:
        db_table = "Способ_распыления"
    name = models.CharField(max_length=100)
    

class FillingMethodOption(models.Model):
    class Meta:
        db_table = "Метод_получения"
    method = models.ForeignKey(FillingMethod, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bool_fil = models.BooleanField(default=False)



class PowderClass(models.Model):
    class Meta:
        db_table = "Класс_пороха"
    name = models.CharField(max_length=100)


class PowderType(models.Model):
    class Meta:
        db_table = "Вид_пороха"
    powder_type = models.ForeignKey(PowderClass, on_delete=models.CASCADE)
    filling_method = models.ForeignKey(FillingMethodOption, on_delete=models.CASCADE)
   





# =========================
# Порох
# =========================




class PowderAnalog(models.Model):
    class Meta:
        db_table = "Аналоги_пороха"
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, related_name='analogs')
    analog = models.ForeignKey(PowderType, on_delete=models.CASCADE, related_name='analog_of')


# =========================
# Свойства
# =========================

class Property(models.Model):
    class Meta:
        db_table = "Название_свойства"
    name = models.CharField(max_length=100)


class PropertyValueType(models.Model):
    class Meta:
        db_table = "Тип_значения_свойства"
    name = models.CharField(max_length=100)


class PropertySynonym(models.Model):
    class Meta:
        db_table = "Синонимы_свойства"
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class PropertyValue(models.Model):
    class Meta:
        db_table = "Свойства"
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    property_value = models.ForeignKey(PropertyValueType, on_delete=models.CASCADE)
    text_value = models.CharField(max_length=255, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)





class PowderProperty(models.Model):
    class Meta:
        db_table = "Свойства_пороха"
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)


# =========================
# Физические характеристики пороха
# =========================

class BulkDensity(models.Model):
    class Meta:
        db_table = "Насыпная_плотность_пороха"
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    


class Flowability(models.Model):
    class Meta:
        db_table = "Текучесть_пороха"
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    value = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    bool_fil = models.BooleanField(default=False)


class GranulometricComposition(models.Model):
    class Meta:
        db_table = "Гранулометрический_состав"
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, null=True, blank=True)
    d10 = models.FloatField()
    d50 = models.FloatField()
    d90 = models.FloatField()
    average_value = models.FloatField()
    mass_fraction = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)


# =========================
# Форма частиц
# =========================

class ParticleShape(models.Model):
    class Meta:
        db_table = "Название_формы_частиц"
    name = models.CharField(max_length=100)


class PowderParticleShape(models.Model):
    class Meta:
        db_table = "Форма_частиц"
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    shape = models.ForeignKey(ParticleShape, on_delete=models.CASCADE)
    size_value = models.FloatField()
    interval_min = models.FloatField(null=True, blank=True)
    interval_max = models.FloatField(null=True, blank=True)
    bool_par = models.BooleanField(default=False)


# =========================
# Газы и газовые смеси
# =========================

class Gas(models.Model):
    class Meta:
        db_table = "Газ"
    formula = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    standard = models.CharField(max_length=100)


class ChemicalComponent(models.Model):
    class Meta:
        db_table = "Химический_компонент"
    formula = models.CharField(max_length=50)


class ChemicalDesignationType(models.Model):
    class Meta:
        db_table = "Тип_химического_обозначения"
    name = models.CharField(max_length=100)


class ChemicalDesignation(models.Model):
    class Meta:
        db_table = "Химическое_обозначение"
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE)
    component = models.ForeignKey(ChemicalComponent, on_delete=models.CASCADE)
    designation_type = models.ForeignKey(ChemicalDesignationType, on_delete=models.CASCADE)
    percent_min = models.FloatField()
    percent_max = models.FloatField()
    type = models.CharField(max_length=100)


class GasMixture(models.Model):
    class Meta:
        db_table = "Газовая_смесь"
    formula = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    standard = models.CharField(max_length=100)


class GasMixtureComponent(models.Model):
    class Meta:
        db_table = "Состав_газовой_смеси"
    mixture = models.ForeignKey(GasMixture, on_delete=models.CASCADE)
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE)
    concentration = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)


# =========================
# Металлическая проволока
# =========================

class MetalWire(models.Model):
    class Meta:
        db_table = "Металлическая_проволока"
    diameter_value = models.FloatField()
    diameter_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    interval_min = models.FloatField(null=True, blank=True)


class MetalWireProperty(models.Model):
    class Meta:
        db_table = "Свойства_металлической_проволоки"
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE)
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)


class WireAnalog(models.Model):
    class Meta:
        db_table = "Аналоги_проволоки"
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analogs')
    analog = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analog_of')


# =========================
# Элементный состав
# =========================

class Element(models.Model):
    class Meta:
        db_table = "Элемент"
    name = models.CharField(max_length=100)


class ElementalComposition(models.Model):
    class Meta:
        db_table = "Элементный_состав_проволоки"
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    fraction = models.FloatField()
