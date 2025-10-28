from django.db import models
from django.contrib.auth.models import User
import json


class Configuration(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='configurations',
        verbose_name='Пользователь',
    )

    name = models.CharField(
        max_length=255,
        verbose_name='Название конфигурации'
    )

    config_data = models.JSONField(
        verbose_name='Данные конфигурации',
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )

    class Meta:
        verbose_name = 'Конфигурация парсинга'
        verbose_name_plural = 'Конфигурации парсинга'
        ordering = ['-created_at']
        unique_together = ['user', 'name']  # Уникальное имя для каждого пользователя

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def get_config_value(self, key, default=None):
        """Метод для получения значения по ключу из JSON"""
        return self.config_data.get(key, default)

    def set_config_value(self, key, value):
        """Метод для установки значения в JSON"""
        self.config_data[key] = value
        self.save()

