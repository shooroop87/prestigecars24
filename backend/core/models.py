# backend/core/models.py - ОБНОВЛЕННАЯ ВЕРСИЯ С SHORT_DESCRIPTION
from django.db import models
from django.utils import timezone


class Review(models.Model):
    """
    Модель для хранения отзывов из внешних источников
    """

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    SOURCE_CHOICES = [
        ("google", "Google"),
        ("tripadvisor", "TripAdvisor"),
        ("csv_import", "CSV Import"),
        ("fallback", "Fallback"),
    ]

    # Основные поля отзыва
    external_id = models.CharField(max_length=255, unique=True, db_index=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, db_index=True)
    author_name = models.CharField(max_length=255)
    author_photo_url = models.URLField(blank=True, null=True)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)

    # НОВОЕ ПОЛЕ: Краткое описание/заголовок отзыва
    short_description = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Краткий заголовок отзыва, например: 'Take this tour! Its fantastic!'",
    )

    text = models.TextField()
    review_date = models.DateTimeField()  # Дата написания отзыва
    relative_time_description = models.CharField(max_length=100, blank=True)

    # Системные поля
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(
        default=False, db_index=True
    )  # Для приоритетных отзывов
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Дополнительные данные в JSON
    raw_data = models.JSONField(blank=True, null=True)  # Полные данные от API

    class Meta:
        ordering = ["-is_featured", "-review_date", "-created_at"]
        indexes = [
            models.Index(fields=["source", "is_active"]),
            models.Index(fields=["is_featured", "is_active"]),
            models.Index(fields=["review_date"]),
            models.Index(fields=["external_id"]),
        ]

    def __str__(self):
        if self.short_description:
            return f"{self.author_name} - {self.short_description} ({self.rating}⭐)"
        return f"{self.author_name} - {self.rating}⭐ ({self.source})"

    def update_relative_time(self):
        """Обновляет относительное время"""
        from datetime import datetime

        now = timezone.now()
        diff = now - self.review_date
        days = diff.days

        if days < 1:
            self.relative_time_description = "Today"
        elif days < 7:
            self.relative_time_description = f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            plural = "s" if weeks != 1 else ""
            self.relative_time_description = f"{weeks} week{plural} ago"
        elif days < 365:
            months = days // 30
            plural = "s" if months != 1 else ""
            self.relative_time_description = f"{months} month{plural} ago"
        else:
            years = days // 365
            plural = "s" if years != 1 else ""
            self.relative_time_description = f"{years} year{plural} ago"

    def save(self, *args, **kwargs):
        """Автоматически обновляем relative_time при сохранении"""
        if not self.relative_time_description or kwargs.get(
            "update_relative_time", True
        ):
            self.update_relative_time()
        super().save(*args, **kwargs)

    @classmethod
    def get_stats(cls):
        """Возвращает статистику по отзывам"""
        from django.db.models import Avg, Count

        stats = cls.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=models.Q(is_active=True)),
            featured=Count("id", filter=models.Q(is_featured=True)),
            avg_rating=Avg("rating"),
        )

        # Статистика по источникам
        by_source = dict(cls.objects.values("source").annotate(count=Count("id")))

        # Статистика по рейтингам
        by_rating = dict(cls.objects.values("rating").annotate(count=Count("id")))

        return {
            **stats,
            "by_source": by_source,
            "by_rating": by_rating,
        }


class ReviewImportLog(models.Model):
    """
    Лог импорта отзывов для отслеживания процесса
    """

    SOURCE_CHOICES = [
        ("google", "Google Places"),
        ("tripadvisor", "TripAdvisor"),
        ("csv_import", "CSV Import"),
        ("manual", "Manual"),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="running",
    )

    # Результаты импорта
    reviews_imported = models.IntegerField(default=0)
    reviews_updated = models.IntegerField(default=0)
    reviews_skipped = models.IntegerField(default=0)

    # Дополнительная информация
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # размер в байтах
    total_rows_processed = models.IntegerField(default=0)

    # Сообщения об ошибках
    error_message = models.TextField(blank=True, null=True)
    warnings = models.TextField(blank=True, null=True)  # Предупреждения

    # Настройки импорта
    import_settings = models.JSONField(
        blank=True, null=True
    )  # Сохраняем параметры импорта

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["source", "status"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        return (
            f"{self.get_source_display()} import at {self.started_at} - {self.status}"
        )

    @property
    def duration(self):
        """Возвращает длительность импорта"""
        if self.finished_at and self.started_at:
            delta = self.finished_at - self.started_at
            return delta
        return None

    @property
    def duration_formatted(self):
        """Возвращает форматированную длительность"""
        duration = self.duration
        if not duration:
            return "—"

        total_seconds = int(duration.total_seconds())
        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    @property
    def success_rate(self):
        """Возвращает процент успешности импорта"""
        total = self.reviews_imported + self.reviews_updated + self.reviews_skipped
        if total == 0:
            return 0
        successful = self.reviews_imported + self.reviews_updated
        return (successful / total) * 100

    def mark_as_finished(self, status="success"):
        """Помечает импорт как завершенный"""
        self.status = status
        self.finished_at = timezone.now()
        self.save(update_fields=["status", "finished_at"])

    def add_error(self, error_message):
        """Добавляет сообщение об ошибке"""
        if self.error_message:
            self.error_message += f"\n{error_message}"
        else:
            self.error_message = error_message
        self.save(update_fields=["error_message"])

    def add_warning(self, warning_message):
        """Добавляет предупреждение"""
        if self.warnings:
            self.warnings += f"\n{warning_message}"
        else:
            self.warnings = warning_message
        self.save(update_fields=["warnings"])

    @classmethod
    def get_recent_stats(cls, days=30):
        """Возвращает статистику за последние N дней"""
        from datetime import timedelta

        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=days)
        recent_logs = cls.objects.filter(started_at__gte=cutoff_date)

        return {
            "total": recent_logs.count(),
            "successful": recent_logs.filter(status="success").count(),
            "failed": recent_logs.filter(status="failed").count(),
            "running": recent_logs.filter(status="running").count(),
            "total_imported": sum(log.reviews_imported for log in recent_logs),
            "total_updated": sum(log.reviews_updated for log in recent_logs),
        }
