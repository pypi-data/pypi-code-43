from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class VitalsFieldMixin(models.Model):
    weight = models.DecimalField(
        verbose_name="Weight:",
        validators=[MinValueValidator(20), MaxValueValidator(150)],
        decimal_places=1,
        max_digits=4,
        help_text="kg",
    )

    # 9
    sys_blood_pressure = models.IntegerField(
        verbose_name="Blood pressure: systolic",
        validators=[MinValueValidator(50), MaxValueValidator(220)],
        help_text="in mm. format SYS, e.g. 120",
    )

    # 9
    dia_blood_pressure = models.IntegerField(
        verbose_name="Blood pressure: diastolic",
        validators=[MinValueValidator(20), MaxValueValidator(150)],
        help_text="in Hg. format DIA, e.g. 80",
    )

    # 10
    heart_rate = models.IntegerField(
        verbose_name="Heart rate:",
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        help_text="BPM",
    )

    # 11
    respiratory_rate = models.IntegerField(
        verbose_name="Respiratory rate:",
        validators=[MinValueValidator(6), MaxValueValidator(50)],
        help_text="breaths/min",
        null=True,
    )

    # 12
    oxygen_saturation = models.IntegerField(
        verbose_name="Oxygen saturation:",
        validators=[MinValueValidator(1), MaxValueValidator(999)],
        help_text="%",
        null=True,
    )

    temperature = models.DecimalField(
        verbose_name="Temperature:",
        validators=[MinValueValidator(30), MaxValueValidator(45)],
        decimal_places=1,
        max_digits=3,
        help_text="in degrees Celcius",
    )

    class Meta:
        abstract = True
