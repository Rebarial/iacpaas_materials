from django.db import models

# =========================
# Справочники
# =========================

class Unit(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FillingMethod(models.Model):
    name = models.CharField(max_length=100)


class FillingMethodOption(models.Model):
    method = models.ForeignKey(FillingMethod, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bool_fil = models.BooleanField(default=False)



class PowderClass(models.Model):
    name = models.CharField(max_length=100)


class PowderType(models.Model):
    powder_type = models.ForeignKey(PowderClass, on_delete=models.CASCADE)
    filling_method = models.ForeignKey(FillingMethodOption, on_delete=models.CASCADE)






# =========================
# Порох
# =========================




class PowderAnalog(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, related_name='analogs')
    analog = models.ForeignKey(PowderType, on_delete=models.CASCADE, related_name='analog_of')


# =========================
# Свойства
# =========================

class Property(models.Model):
    name = models.CharField(max_length=100)


class PropertyValueType(models.Model):
    name = models.CharField(max_length=100)


class PropertySynonym(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class PropertyValue(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    property_value = models.ForeignKey(PropertyValueType, on_delete=models.CASCADE)
    text_value = models.CharField(max_length=255, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)





class PowderProperty(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)


# =========================
# Физические характеристики пороха
# =========================

class BulkDensity(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)



class Flowability(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE)
    value = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    bool_fil = models.BooleanField(default=False)


class GranulometricComposition(models.Model):
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
    name = models.CharField(max_length=100)


class PowderParticleShape(models.Model):
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
    formula = models.CharField(max_length=50)
    grade = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    standard = models.CharField(max_length=100)


class ChemicalComponent(models.Model):
    formula = models.CharField(max_length=50)


class ChemicalDesignationType(models.Model):
    name = models.CharField(max_length=100)


class ChemicalDesignation(models.Model):
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE)
    component = models.ForeignKey(ChemicalComponent, on_delete=models.CASCADE)
    designation_type = models.ForeignKey(ChemicalDesignationType, on_delete=models.CASCADE)
    percent_min = models.FloatField()
    percent_max = models.FloatField()
    type = models.CharField(max_length=100)


class GasMixture(models.Model):
    formula = models.CharField(max_length=100)
    grade = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    standard = models.CharField(max_length=100)


class GasMixtureComponent(models.Model):
    mixture = models.ForeignKey(GasMixture, on_delete=models.CASCADE)
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE)
    concentration = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)


# =========================
# Металлическая проволока
# =========================

class MetalWire(models.Model):
    diameter_value = models.FloatField()
    diameter_unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    interval = models.FloatField(null=True, blank=True)


class MetalWireProperty(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE)
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE)


class WireAnalog(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analogs')
    analog = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analog_of')


# =========================
# Элементный состав
# =========================

class Element(models.Model):
    name = models.CharField(max_length=100)


class ElementalComposition(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE)
    element = models.ForeignKey(Element, on_delete=models.CASCADE)
    fraction = models.FloatField()
