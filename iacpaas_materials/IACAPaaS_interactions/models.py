from django.db import models

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

# =========================
# Порошки
# =========================

class PowderClass(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Класс порошка"
        verbose_name_plural = "Классы порошков"

class Powder(models.Model):
    powder_class = models.ForeignKey(PowderClass, on_delete=models.CASCADE, verbose_name="Класс порошка")
    name = models.CharField("Название", max_length=100)
    adress_pow = models.CharField("Источник", max_length=200)
    date_pow = models.DateTimeField("Дата внесения", auto_now_add=True)
    standards = models.CharField("Стандарты", max_length=300)

    def __str__(self):
        return f"{self.powder_class}"

    class Meta:
        verbose_name = "Порошок"
        verbose_name_plural = "Порошок"

class ElementalComposition_powder(models.Model):
    wire = models.ForeignKey(Powder, on_delete=models.CASCADE, verbose_name="Порошок")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Элемент")
    fraction = models.FloatField("Массовая доля")

    class Meta:
        verbose_name = "Элементный состав проволоки"
        verbose_name_plural = "Элементный состав проволоки"

class Particle_form(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, verbose_name="Порошок")
    name = models.CharField("Название опции", max_length=100)
    obtaining_method = models.CharField("Метод получения", max_length=300)

    def __str__(self):
        return f"{self.powder} — {self.name}"

    class Meta:
        verbose_name = "Форма частиц"
        verbose_name_plural = "Форма частиц"

class PowderAnalog(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, related_name='analogs', verbose_name="Порошок")
    analog = models.ForeignKey(Powder, on_delete=models.CASCADE, related_name='analog_of', verbose_name="Аналог")

    class Meta:
        verbose_name = "Аналог порошка"
        verbose_name_plural = "Аналоги порошков"

class PowdePropery(models.Model):
    name = models.CharField("Название", max_length=200)

class PowderPropertyValue(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, verbose_name="Порошок")
    property = models.ForeignKey(PowdePropery, on_delete=models.CASCADE, verbose_name="Свойство")
    property_value = models.CharField("Значение", max_length=100)

    class Meta:
        verbose_name = "Свойство порошка"
        verbose_name_plural = "Свойства порошков"

# =========================
# Газы и газовые смеси
# =========================

class Gas(models.Model):
    name_gas = models.CharField("Название", max_length=100)
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
    formula = models.CharField("Формула", max_length=150)

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
    percent_value = models.CharField("Мин. %", max_length=100)


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

    class Meta:
        verbose_name = "Компонент газовой смеси"
        verbose_name_plural = "Компоненты газовых смесей"

# =========================
# Металлическая проволока
# =========================

class MetalWire(models.Model):
    name_wire = models.CharField("Марка", max_length=50)
    diameter_value = models.CharField("Диаметр", max_length=50)

    adress_wire = models.CharField("Источник", max_length=200)
    date_wire = models.DateTimeField("Дата внесения", auto_now_add=True)
    def __str__(self):
        return f"Проволока Ø{self.diameter_value} {self.diameter_unit}"

    class Meta:
        verbose_name = "Металлическая проволока"
        verbose_name_plural = "Металлическая проволока"

class MetalWire_diametrs(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    value = models.FloatField("Значение диаметра")

class MetalWireProperty(models.Model):
    name = models.CharField("Название", max_length=200)

class MetalWirePropertyValue(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    property = models.ForeignKey(MetalWireProperty, on_delete=models.CASCADE, verbose_name="Свойство")
    property_value = models.CharField("Значение", max_length=200)

    class Meta:
        verbose_name = "Свойство проволоки"
        verbose_name_plural = "Свойства проволоки"

class WireAnalog(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analogs', verbose_name="Проволока")
    analog = models.ForeignKey(MetalWire, on_delete=models.CASCADE, related_name='analog_of', verbose_name="Аналог")

    class Meta:
        verbose_name = "Аналог проволоки"
        verbose_name_plural = "Аналоги проволоки"

class ElementalComposition_wire(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Элемент")
    fraction = models.FloatField("Массовая доля")

    class Meta:
        verbose_name = "Элементный состав проволоки"
        verbose_name_plural = "Элементный состав проволоки"

# =========================
# Металлическая проволока
# =========================

class MetalClass(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Класс сплава"
        verbose_name_plural = "Классы сплавов"

class Metal(models.Model):
    metal_class = models.ForeignKey(MetalClass, on_delete=models.CASCADE, verbose_name="Класс сплава")
    adress_pow = models.CharField("Источник", max_length=200)
    date_pow = models.DateTimeField("Дата внесения", auto_now_add=True)
    standards = models.CharField("Стандарты", max_length=300)

    def __str__(self):
        return f"{self.powder_class}"

    class Meta:
        verbose_name = "Тип порошка"
        verbose_name_plural = "Типы порошков"

class MetalPropery(models.Model):
    name = models.CharField("Название", max_length=200)

class MetalPropertyValue(models.Model):
    metal = models.ForeignKey(Metal, on_delete=models.CASCADE, verbose_name="Металл")
    property = models.ForeignKey(MetalPropery, on_delete=models.CASCADE, verbose_name="Свойство")
    property_value = models.CharField("Значение", max_length=200)

    class Meta:
        verbose_name = "Свойство металла"
        verbose_name_plural = "Свойства металла"


