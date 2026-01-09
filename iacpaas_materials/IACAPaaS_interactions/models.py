from django.db import models

# =========================
# Справочники
# =========================

class Unit(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"


class FillingMethod(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Метод заполнения"
        verbose_name_plural = "Методы заполнения"


class FillingMethodOption(models.Model):
    method = models.ForeignKey(FillingMethod, on_delete=models.CASCADE, verbose_name="Метод заполнения")
    name = models.CharField("Название опции", max_length=100)
    bool_fil = models.BooleanField("Флаг заполнения", default=False)
    
    def __str__(self):
        return f"{self.method} — {self.name}"

    class Meta:
        verbose_name = "Опция метода заполнения"
        verbose_name_plural = "Опции методов заполнения"


class PowderClass(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Класс порошка"
        verbose_name_plural = "Классы порошков"


class PowderType(models.Model):
    powder_type = models.ForeignKey(PowderClass, on_delete=models.CASCADE, verbose_name="Класс порошка")
    filling_method = models.ForeignKey(FillingMethodOption, on_delete=models.CASCADE, verbose_name="Метод заполнения")
    adress_pow = models.CharField("Источник", max_length=200)
    date_pow = models.DateTimeField("Дата внесения", auto_now_add=True)
    def __str__(self):
        return f"{self.powder_type} — {self.filling_method}"

    class Meta:
        verbose_name = "Тип порошка"
        verbose_name_plural = "Типы порошков"


# =========================
# Порох (Аналоги)
# =========================

class PowderAnalog(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, related_name='analogs', verbose_name="Порошок")
    analog = models.ForeignKey(PowderType, on_delete=models.CASCADE, related_name='analog_of', verbose_name="Аналог")

    class Meta:
        verbose_name = "Аналог порошка"
        verbose_name_plural = "Аналоги порошков"


# =========================
# Свойства
# =========================

class Property(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Свойство"
        verbose_name_plural = "Свойства"


class PropertyValueType(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип значения свойства"
        verbose_name_plural = "Типы значений свойств"


class PropertySynonym(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Свойство")
    name = models.CharField("Синоним", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Синоним свойства"
        verbose_name_plural = "Синонимы свойств"


class PropertyValue(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Свойство")
    property_value = models.ForeignKey(PropertyValueType, on_delete=models.CASCADE, verbose_name="Тип значения")
    text_value = models.CharField("Текстовое значение", max_length=255, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Единица измерения")
    
    def __str__(self):
        return f"{self.property}: {self.text_value or self.property_value}"

    class Meta:
        verbose_name = "Значение свойства"
        verbose_name_plural = "Значения свойств"


class PowderProperty(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, verbose_name="Тип порошка")
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE, verbose_name="Значение свойства")

    class Meta:
        verbose_name = "Свойство порошка"
        verbose_name_plural = "Свойства порошков"


# =========================
# Физические характеристики пороха
# =========================

class BulkDensity(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, verbose_name="Тип порошка")
    value = models.CharField("Значение", max_length=255, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения")

    class Meta:
        verbose_name = "Насыпная плотность"
        verbose_name_plural = "Насыпная плотность"


class Flowability(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, verbose_name="Тип порошка")
    value = models.FloatField("Значение")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения")
    bool_fil = models.BooleanField("Флаг заполнения", default=False)

    class Meta:
        verbose_name = "Сыпучесть"
        verbose_name_plural = "Сыпучесть"


class GranulometricComposition(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, verbose_name="Тип порошка")
    value = models.CharField("Значение", max_length=255, null=True, blank=True)
    d10 = models.FloatField("D10")
    d50 = models.FloatField("D50")
    d90 = models.FloatField("D90")
    average_value = models.FloatField("Среднее значение")
    mass_fraction = models.FloatField("Массовая доля")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения")

    class Meta:
        verbose_name = "Гранулометрический состав"
        verbose_name_plural = "Гранулометрический состав"


# =========================
# Форма частиц
# =========================

class ParticleShape(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Форма частицы"
        verbose_name_plural = "Формы частиц"


class PowderParticleShape(models.Model):
    powder = models.ForeignKey(PowderType, on_delete=models.CASCADE, verbose_name="Тип порошка")
    shape = models.ForeignKey(ParticleShape, on_delete=models.CASCADE, verbose_name="Форма")
    size_value = models.FloatField("Размер")
    value_powder = models.FloatField("Значение", null=True, blank=True)
    
    bool_par = models.BooleanField("Флаг формы", default=False)

    class Meta:
        verbose_name = "Форма частиц порошка"
        verbose_name_plural = "Формы частиц порошка"


# =========================
# Газы и газовые смеси
# =========================

class Gas(models.Model):
    name_gas = models.CharField("Формула", max_length=100)
    formula = models.CharField("Формула", max_length=50)
    grade = models.CharField("Марка", max_length=50)
    brand = models.CharField("Бренд", max_length=50)
    standard = models.CharField("Стандарт", max_length=100)
    adress_gas = models.CharField("Источник", max_length=200)
    date_gas = models.DateTimeField("Дата внесения", auto_now_add=True)
    def __str__(self):
        return f"{self.formula} ({self.brand})"

    class Meta:
        verbose_name = "Газ"
        verbose_name_plural = "Газы"


class ChemicalComponent(models.Model):
    formula = models.CharField("Формула", max_length=50)

    def __str__(self):
        return self.formula

    class Meta:
        verbose_name = "Химический компонент"
        verbose_name_plural = "Химические компоненты"


class ChemicalDesignationType(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип обозначения химсостава"
        verbose_name_plural = "Типы обозначений химсостава"


class ChemicalDesignation(models.Model):
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE, verbose_name="Газ")
    component = models.ForeignKey(ChemicalComponent, on_delete=models.CASCADE, verbose_name="Компонент")
    designation_type = models.ForeignKey(ChemicalDesignationType, on_delete=models.CASCADE, verbose_name="Тип обозначения")
    percent_value = models.FloatField("Мин. %")
    

    class Meta:
        verbose_name = "Химическое обозначение газа"
        verbose_name_plural = "Химические обозначения газов"


class GasMixture(models.Model):
    formula = models.CharField("Формула", max_length=100)
    grade = models.CharField("Марка", max_length=50)
    brand = models.CharField("Бренд", max_length=50)
    standard = models.CharField("Стандарт", max_length=100)

    def __str__(self):
        return f"{self.formula} ({self.brand})"

    class Meta:
        verbose_name = "Газовая смесь"
        verbose_name_plural = "Газовые смеси"


class GasMixtureComponent(models.Model):
    mixture = models.ForeignKey(GasMixture, on_delete=models.CASCADE, verbose_name="Смесь")
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE, verbose_name="Газ")
    concentration = models.FloatField("Концентрация")
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения")

    class Meta:
        verbose_name = "Компонент газовой смеси"
        verbose_name_plural = "Компоненты газовых смесей"


# =========================
# Металлическая проволока
# =========================

class MetalWire(models.Model):
    diameter_value = models.FloatField("Диаметр")
    diameter_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения диаметра")
    interval = models.FloatField("Интервал", null=True, blank=True)

    def __str__(self):
        return f"Проволока Ø{self.diameter_value} {self.diameter_unit}"

    class Meta:
        verbose_name = "Металлическая проволока"
        verbose_name_plural = "Металлическая проволока"


class MetalWireProperty(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE, verbose_name="Значение свойства")
    adress_wire = models.CharField("Источник", max_length=200)
    date_wire = models.DateTimeField("Дата внесения", auto_now_add=True)
    class Meta:
        verbose_name = "Свойство проволоки"
        verbose_name_plural = "Свойства проволоки"


class WireAnalog(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analogs', verbose_name="Проволока")
    analog = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analog_of', verbose_name="Аналог")

    class Meta:
        verbose_name = "Аналог проволоки"
        verbose_name_plural = "Аналоги проволоки"


# =========================
# Элементный состав
# =========================

class Element(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Химический элемент"
        verbose_name_plural = "Химические элементы"


class ElementalComposition(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Элемент")
    fraction = models.FloatField("Массовая доля")

    class Meta:
        verbose_name = "Элементный состав проволоки"
        verbose_name_plural = "Элементный состав проволоки"
