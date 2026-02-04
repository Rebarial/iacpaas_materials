from django.db import models

# =========================
# Терминология
# =========================

class TerminType(models.Model):

    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Termin(models.Model):
    name = models.CharField(max_length=250)
    termin_type = models.ForeignKey(TerminType, null=True, blank=True, on_delete=models.SET_NULL)

    in_iacpaas = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# =========================
# Элементный состав
# =========================

class Element(models.Model):

    TYPE_CHOICES = [
        ('element', 'Элемент'),
        ('compound_element', 'Составной элемент'),
        ('simple_substance', 'Простое вещество'),
        ('complex_substance', 'Сложное вещество'),
    ]

    formula =models.CharField("Формула", max_length=100)
    name = models.CharField("Название", max_length=100)
    element_type = models.CharField(
        "Тип",
        max_length=20,
        choices=TYPE_CHOICES,
        blank=True,
        null=True
    )
    in_iacpaas = models.BooleanField(default=False)

    def __str__(self):
        return self.formula

    def save(self, *args, **kwargs):
        if not self.element_type:
            self.element_type = self.determine_type()

        self.formula = self.convert_to_subscript(self.formula)

        super().save(*args, **kwargs)

    @staticmethod
    def convert_to_subscript(text):
        """Преобразует цифры в тексте в подстрочные индексы"""
        subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        }
        return ''.join(subscript_map.get(c, c) for c in text)

    def determine_type(self):
        formula = self.formula

        if '+' in formula:
            return 'compound_element'

        import re
        parts = re.split(r'\d+', formula)
        parts = [p for p in parts if p]

        has_digits = any(c.isdigit() for c in formula)
        if has_digits and len(parts) == 1:
            return 'simple_substance'

        return 'complex_substance'

    class Meta:
        verbose_name = "Химический элемент"
        verbose_name_plural = "Химические элементы"

# =========================
# Свойства
# =========================

class PropertyType(models.Model):
    name = models.CharField("Название", max_length=200)
    in_iacpaas = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Property(models.Model):
    name = models.CharField("Название", max_length=200)
    type = models.ForeignKey(PropertyType, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Класс свойства")
    in_iacpaas = models.BooleanField(default=False)

    @property
    def is_synonym(self):
        """Проверяет, является ли название свойства синонимом другого свойства"""
        return PropertySynonym.objects.filter(name=self.name).exists()

    @property
    def original(self):
        """Возвращает оригинальное свойство, если текущее является синонимом"""
        try:
            synonym = PropertySynonym.objects.get(name=self.name)
            return synonym.property
        except PropertySynonym.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.type} - {self.name}"

class PropertySynonym(models.Model):
    name = models.CharField("Синоним", max_length=200)
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="synonyms",
        verbose_name="Свойство"
    )

    def __str__(self):
        return f"{self.name} → {self.property.name}"

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
    adress= models.CharField("Источник", max_length=200)
    date = models.DateTimeField("Дата внесения", auto_now_add=True)
    standards = models.CharField("Стандарты", max_length=300)

    def __str__(self):
        return f"{self.powder_class}"

    class Meta:
        verbose_name = "Порошок"
        verbose_name_plural = "Порошок"

class ElementalComposition_powder(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, verbose_name="Порошок")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Элемент")
    fraction = models.FloatField("Массовая доля")

    class Meta:
        verbose_name = "Элементный состав порошка"
        verbose_name_plural = "Элементный состав порошка"

class Particle_form(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, verbose_name="Порошок")
    termin = models.ForeignKey(Termin, on_delete=models.CASCADE, verbose_name="Термин")
    obtaining_method = models.CharField("Метод получения", max_length=300)

    def __str__(self):
        return f"{self.powder} — {self.termin.name}"

    class Meta:
        verbose_name = "Форма частиц"
        verbose_name_plural = "Форма частиц"

class PowderAnalog(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, related_name='analogs', verbose_name="Порошок")
    analog = models.ForeignKey(Powder, on_delete=models.CASCADE, related_name='analog_of', verbose_name="Аналог")

    class Meta:
        verbose_name = "Аналог порошка"
        verbose_name_plural = "Аналоги порошков"

class PowderPropertyValue(models.Model):
    powder = models.ForeignKey(Powder, on_delete=models.CASCADE, verbose_name="Порошок")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Свойство")
    property_value = models.FloatField("Значение")
    unit = models.CharField("ед.изм", max_length=100, blank=True, null=True, default="")

    class Meta:
        verbose_name = "Свойство порошка"
        verbose_name_plural = "Свойства порошков"

# =========================
# Газы и газовые смеси
# =========================

class Gas(models.Model):
    name = models.CharField("Название", max_length=100)
    formula = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Элемент")
    grade = models.CharField("Марка", max_length=50)
    brand = models.CharField("Бренд", max_length=50)
    standards = models.CharField("Стандарты", max_length=300)
    adress = models.CharField("Источник", max_length=200)
    date = models.DateTimeField("Дата внесения", auto_now_add=True)
    def __str__(self):
        return f"{self.formula} ({self.brand})"

    class Meta:
        verbose_name = "Газ"
        verbose_name_plural = "Газы"

class ChemicalDesignation(models.Model):
    gas = models.ForeignKey(Gas, on_delete=models.CASCADE, verbose_name="Газ")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Компонент")
    percent_value = models.FloatField("Массовая доля")

    class Meta:
        verbose_name = "Химическое обозначение газа"
        verbose_name_plural = "Химические обозначения газов"

class GasMixture(models.Model):
    formula = models.CharField("Формула", max_length=100)
    grade = models.CharField("Марка", max_length=50)
    brand = models.CharField("Бренд", max_length=50)
    standards = models.CharField("Стандарты", max_length=300)
    adress = models.CharField("Источник", max_length=200)

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

class MetalWireClass(models.Model):
    name = models.CharField("Название", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Класс проволки"
        verbose_name_plural = "Классы проволки"


class MetalWire(models.Model):
    name = models.CharField("Марка", max_length=50)
    wire_class = models.ForeignKey(MetalWireClass, on_delete=models.CASCADE, verbose_name="Класс проволки")
    adress = models.CharField("Источник", max_length=200)
    date = models.DateTimeField("Дата внесения", auto_now_add=True)
    standards = models.CharField("Стандарты", max_length=300)


    def __str__(self):
        return f"Проволока {self.name}"

    class Meta:
        verbose_name = "Металлическая проволока"
        verbose_name_plural = "Металлическая проволока"

class MetalWire_diametrs(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    value = models.FloatField("Значение диаметра")

class MetalWirePropertyValue(models.Model):
    wire = models.ForeignKey(MetalWire, on_delete=models.CASCADE, verbose_name="Проволока")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Свойство")
    value = models.FloatField("Значение")
    unit = models.CharField("ед.изм", max_length=100, blank=True, null=True)

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
    name = models.CharField("Название", max_length=200)
    adress = models.CharField("Источник", max_length=200)
    date = models.DateTimeField("Дата внесения", auto_now_add=True)
    standards = models.CharField("Стандарты", max_length=300)

    def __str__(self):
        return f"{self.metal_class.name}  {self.name}"

    class Meta:
        verbose_name = "Металл"
        verbose_name_plural = "Металл"

class MetalPropertyValue(models.Model):
    metal = models.ForeignKey(Metal, on_delete=models.CASCADE, verbose_name="Металл")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Свойство")
    value = models.FloatField("Значение")
    unit = models.CharField("ед.изм", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Свойство металла"
        verbose_name_plural = "Свойства металла"

class ElementalComposition_metal(models.Model):
    metal = models.ForeignKey(Metal, on_delete=models.CASCADE, verbose_name="Металл")
    element = models.ForeignKey(Element, on_delete=models.CASCADE, verbose_name="Элемент")
    fraction = models.FloatField("Массовая доля")

    class Meta:
        verbose_name = "Элементный состав металла"
        verbose_name_plural = "Элементный состав металла"

