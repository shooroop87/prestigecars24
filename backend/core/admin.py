# backend/core/admin.py - С ПОДДЕРЖКОЙ SHORT_DESCRIPTION
import csv
import io
import json
from datetime import datetime

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Review, ReviewImportLog


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "author_name_short",
        "short_description_preview",  # НОВОЕ ПОЛЕ
        "rating_stars",
        "source_badge",
        "text_preview",
        "review_date",
        "relative_time_description",
        "is_featured",
        "is_active",
    ]
    list_filter = [
        "source",
        "rating",
        "is_active",
        "is_featured",
        "review_date",
        "created_at",
    ]
    search_fields = [
        "author_name",
        "text",
        "external_id",
        "short_description",
    ]  # ДОБАВЛЕНО
    readonly_fields = ["external_id", "created_at", "updated_at", "raw_data_preview"]
    list_editable = ["is_featured", "is_active"]
    date_hierarchy = "review_date"
    list_per_page = 25

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "external_id",
                    "source",
                    "author_name",
                    "author_photo_url",
                    "rating",
                    "short_description",  # НОВОЕ ПОЛЕ В ФОРМЕ
                    "text",
                )
            },
        ),
        (
            "Даты",
            {
                "fields": (
                    "review_date",
                    "relative_time_description",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        ("Настройки", {"fields": ("is_active", "is_featured")}),
        (
            "Техническая информация",
            {"fields": ("raw_data_preview",), "classes": ("collapse",)},
        ),
    )

    actions = [
        "make_featured",
        "make_not_featured",
        "activate_reviews",
        "deactivate_reviews",
        "update_relative_time",
        "export_selected_to_csv",
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-csv/", self.import_csv_view, name="core_review_import_csv"),
            path("export-csv/", self.export_csv_view, name="core_review_export_csv"),
            path(
                "validate-csv/", self.validate_csv_ajax, name="core_review_validate_csv"
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        """Добавляем кнопки импорта/экспорта в changelist"""
        extra_context = extra_context or {}
        extra_context.update(
            {
                "import_csv_url": reverse("admin:core_review_import_csv"),
                "export_csv_url": reverse("admin:core_review_export_csv"),
                "show_import_button": True,
            }
        )
        return super().changelist_view(request, extra_context)

    def validate_csv_ajax(self, request):
        """AJAX валидация CSV файла перед импортом"""
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed"}, status=405)

        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            return JsonResponse({"error": "Файл не выбран"}, status=400)

        try:
            content = csv_file.read().decode("utf-8")
            csv_file.seek(0)

            reader = csv.DictReader(io.StringIO(content))

            required_fields = ["external_id", "author_name", "text", "rating"]
            missing_fields = [
                field for field in required_fields if field not in reader.fieldnames
            ]

            if missing_fields:
                return JsonResponse(
                    {
                        "error": f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
                    },
                    status=400,
                )

            total_rows = 0
            valid_rows = 0
            errors = []

            for i, row in enumerate(reader, 1):
                total_rows += 1

                if not all(
                    [row.get("external_id"), row.get("author_name"), row.get("text")]
                ):
                    errors.append(f"Строка {i}: пустые обязательные поля")
                    continue

                try:
                    rating = int(row.get("rating", 5))
                    if not 1 <= rating <= 5:
                        errors.append(f"Строка {i}: рейтинг должен быть от 1 до 5")
                        continue
                except (ValueError, TypeError):
                    errors.append(f"Строка {i}: некорректный рейтинг")
                    continue

                valid_rows += 1

                if len(errors) >= 10:
                    errors.append("... и другие ошибки")
                    break

            return JsonResponse(
                {
                    "valid": len(errors) == 0,
                    "total_rows": total_rows,
                    "valid_rows": valid_rows,
                    "errors": errors[:10],
                    "fields": reader.fieldnames,
                }
            )

        except Exception as e:
            return JsonResponse(
                {"error": f"Ошибка обработки файла: {str(e)}"}, status=400
            )

    def import_csv_view(self, request):
        """Импорт CSV с валидацией и отчетом"""
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                messages.error(request, "Выберите CSV файл")
                return HttpResponseRedirect("..")

            update_existing = request.POST.get("update_existing", False)
            test_mode = request.POST.get("test_mode", False)

            try:
                with transaction.atomic():
                    import_log = ReviewImportLog.objects.create(
                        source="csv_import", status="running"
                    )

                    content = csv_file.read().decode("utf-8")
                    reader = csv.DictReader(io.StringIO(content))

                    imported = 0
                    updated = 0
                    skipped = 0
                    errors = []

                    for i, row in enumerate(reader, 1):
                        try:
                            if not all(
                                [
                                    row.get("external_id"),
                                    row.get("author_name"),
                                    row.get("text"),
                                ]
                            ):
                                skipped += 1
                                errors.append(f"Строка {i}: пустые обязательные поля")
                                continue

                            review_date = self._parse_date(row.get("review_date"))
                            raw_data = self._parse_raw_data(row.get("raw_data"))

                            review_data = {
                                "source": row.get("source", "tripadvisor"),
                                "author_name": row["author_name"][:255],
                                "author_photo_url": row.get("author_photo_url", ""),
                                "rating": int(row.get("rating", 5)),
                                "short_description": row.get("short_description", "")[
                                    :200
                                ],  # НОВОЕ ПОЛЕ
                                "text": row["text"],
                                "review_date": review_date,
                                "relative_time_description": row.get(
                                    "relative_time_description", ""
                                ),
                                "is_active": str(row.get("is_active", "True")).lower()
                                == "true",
                                "is_featured": str(
                                    row.get("is_featured", "False")
                                ).lower()
                                == "true",
                                "raw_data": raw_data,
                            }

                            if not 1 <= review_data["rating"] <= 5:
                                skipped += 1
                                errors.append(f"Строка {i}: некорректный рейтинг")
                                continue

                            if test_mode:
                                if Review.objects.filter(
                                    external_id=row["external_id"]
                                ).exists():
                                    if update_existing:
                                        updated += 1
                                    else:
                                        skipped += 1
                                else:
                                    imported += 1
                            else:
                                review, created = Review.objects.get_or_create(
                                    external_id=row["external_id"], defaults=review_data
                                )

                                if created:
                                    imported += 1
                                elif update_existing:
                                    Review.objects.filter(id=review.id).update(
                                        **review_data
                                    )
                                    updated += 1
                                else:
                                    skipped += 1

                        except Exception as e:
                            errors.append(f"Строка {i}: {str(e)}")
                            skipped += 1

                    import_log.reviews_imported = imported
                    import_log.reviews_updated = updated
                    import_log.reviews_skipped = skipped
                    import_log.status = "success"
                    import_log.finished_at = timezone.now()

                    if errors:
                        import_log.error_message = "\n".join(errors[:20])

                    import_log.save()

                    if test_mode:
                        messages.info(
                            request,
                            mark_safe(
                                f"""
                            <strong>Тестовый режим - изменения не применены:</strong><br>
                            • Будет создано: {imported}<br>
                            • Будет обновлено: {updated}<br>
                            • Будет пропущено: {skipped}<br>
                            • Ошибок: {len(errors)}
                            """
                            ),
                        )
                    else:
                        messages.success(
                            request,
                            mark_safe(
                                f"""
                            <strong>Импорт завершен успешно!</strong><br>
                            • Создано: {imported}<br>
                            • Обновлено: {updated}<br>
                            • Пропущено: {skipped}<br>
                            • Ошибок: {len(errors)}
                            """
                            ),
                        )

                    if errors:
                        messages.warning(
                            request,
                            f"Обнаружены ошибки в {len(errors)} строках. Подробности в логе импорта.",
                        )

            except Exception as e:
                messages.error(request, f"Критическая ошибка импорта: {str(e)}")
                if "import_log" in locals():
                    import_log.status = "failed"
                    import_log.error_message = str(e)
                    import_log.finished_at = timezone.now()
                    import_log.save()

            return HttpResponseRedirect("..")

        context = {
            "title": "Импорт отзывов из CSV",
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(request),
        }
        return render(request, "admin/csv_import_form.html", context)

    def export_csv_view(self, request):
        """Экспорт отзывов в CSV"""
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="reviews_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )

        response.write("\ufeff")  # BOM для Excel

        writer = csv.writer(response)

        headers = [
            "external_id",
            "source",
            "author_name",
            "author_photo_url",
            "rating",
            "short_description",  # НОВОЕ ПОЛЕ В ЭКСПОРТЕ
            "text",
            "review_date",
            "relative_time_description",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
            "raw_data",
        ]
        writer.writerow(headers)

        queryset = self.get_queryset(request)

        for review in queryset.iterator():
            writer.writerow(
                [
                    review.external_id,
                    review.source,
                    review.author_name,
                    review.author_photo_url or "",
                    review.rating,
                    review.short_description or "",  # НОВОЕ ПОЛЕ В ЭКСПОРТЕ
                    review.text,
                    review.review_date.strftime("%Y-%m-%d %H:%M:%S"),
                    review.relative_time_description,
                    review.is_active,
                    review.is_featured,
                    review.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    review.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                    (
                        json.dumps(review.raw_data, ensure_ascii=False)
                        if review.raw_data
                        else ""
                    ),
                ]
            )

        return response

    def _parse_date(self, date_str):
        """Парсинг даты из CSV"""
        if not date_str:
            return timezone.now()

        try:
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d.%m.%Y %H:%M:%S",
                "%d.%m.%Y",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y",
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
                except ValueError:
                    continue

            parsed = parse_datetime(date_str)
            if parsed:
                return parsed

        except Exception:
            pass

        return timezone.now()

    def _parse_raw_data(self, raw_data_str):
        """Парсинг JSON из поля raw_data"""
        if not raw_data_str:
            return {}

        try:
            if raw_data_str.startswith("{") and raw_data_str.endswith("}"):
                import ast

                try:
                    return ast.literal_eval(raw_data_str)
                except:
                    pass

            return json.loads(raw_data_str)
        except Exception:
            return {"original": raw_data_str}

    # НОВЫЙ МЕТОД ДЛЯ ОТОБРАЖЕНИЯ SHORT_DESCRIPTION
    def short_description_preview(self, obj):
        if not obj.short_description:
            return format_html('<span style="color: #999;">—</span>')
        desc = obj.short_description
        preview = desc[:40] + "..." if len(desc) > 40 else desc
        return format_html(
            '<span title="{}" style="font-weight: bold; color: #2196F3;">{}</span>',
            desc,
            preview,
        )

    short_description_preview.short_description = "Краткое описание"

    # Display методы
    def author_name_short(self, obj):
        name = obj.author_name or "Аноним"
        return name[:20] + "..." if len(name) > 20 else name

    author_name_short.short_description = "Автор"

    def rating_stars(self, obj):
        stars = "⭐" * obj.rating
        return format_html('<span title="{}/5">{}</span>', obj.rating, stars)

    rating_stars.short_description = "Рейтинг"

    def source_badge(self, obj):
        colors = {"google": "#4285F4", "tripadvisor": "#00AA6C", "fallback": "#6c757d"}
        color = colors.get(obj.source, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_source_display(),
        )

    source_badge.short_description = "Источник"

    def text_preview(self, obj):
        text = obj.text or ""
        preview = text[:60] + "..." if len(text) > 60 else text
        return format_html('<span title="{}">{}</span>', text, preview)

    text_preview.short_description = "Текст"

    def raw_data_preview(self, obj):
        if not obj.raw_data:
            return "Нет данных"
        try:
            formatted = json.dumps(obj.raw_data, indent=2, ensure_ascii=False)
            return format_html(
                "<pre>{}</pre>",
                formatted[:500] + "..." if len(formatted) > 500 else formatted,
            )
        except Exception:
            return str(obj.raw_data)[:500]

    raw_data_preview.short_description = "Сырые данные"

    # Actions
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} отзывов помечены как избранные")

    make_featured.short_description = "Сделать избранными"

    def make_not_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} отзывов убраны из избранных")

    make_not_featured.short_description = "Убрать из избранных"

    def activate_reviews(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} отзывов активированы")

    activate_reviews.short_description = "Активировать"

    def deactivate_reviews(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} отзывов деактивированы")

    deactivate_reviews.short_description = "Деактивировать"

    def update_relative_time(self, request, queryset):
        updated = 0
        for review in queryset:
            old_time = review.relative_time_description
            review.update_relative_time()
            if old_time != review.relative_time_description:
                review.save(update_fields=["relative_time_description"])
                updated += 1
        self.message_user(request, f"Обновлено relative_time для {updated} отзывов")

    update_relative_time.short_description = "Обновить relative_time"

    def export_selected_to_csv(self, request, queryset):
        """Экспорт выбранных отзывов"""
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="selected_reviews_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )
        response.write("\ufeff")  # BOM

        writer = csv.writer(response)
        headers = [
            "external_id",
            "source",
            "author_name",
            "rating",
            "short_description",  # НОВОЕ ПОЛЕ
            "text",
            "review_date",
            "is_active",
            "is_featured",
        ]
        writer.writerow(headers)

        for review in queryset:
            writer.writerow(
                [
                    review.external_id,
                    review.source,
                    review.author_name,
                    review.rating,
                    review.short_description or "",  # НОВОЕ ПОЛЕ
                    review.text,
                    review.review_date.strftime("%Y-%m-%d %H:%M:%S"),
                    review.is_active,
                    review.is_featured,
                ]
            )

        return response

    export_selected_to_csv.short_description = "Экспорт выбранных в CSV"


@admin.register(ReviewImportLog)
class ReviewImportLogAdmin(admin.ModelAdmin):
    list_display = [
        "source",
        "started_at",
        "status_badge",
        "reviews_imported",
        "reviews_updated",
        "reviews_skipped",
        "duration",
    ]
    list_filter = ["source", "status", "started_at"]
    readonly_fields = [
        "source",
        "started_at",
        "finished_at",
        "status",
        "reviews_imported",
        "reviews_updated",
        "reviews_skipped",
        "error_message_formatted",
    ]

    def status_badge(self, obj):
        colors = {"running": "#ffc107", "success": "#28a745", "failed": "#dc3545"}
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.status.upper(),
        )

    status_badge.short_description = "Статус"

    def duration(self, obj):
        if obj.finished_at and obj.started_at:
            delta = obj.finished_at - obj.started_at
            return f"{delta.total_seconds():.1f}s"
        return "—"

    duration.short_description = "Длительность"

    def error_message_formatted(self, obj):
        if not obj.error_message:
            return "Нет ошибок"
        return format_html("<pre>{}</pre>", obj.error_message[:1000])

    error_message_formatted.short_description = "Ошибки"
