# backend/core/management/commands/import_reviews.py
import os

from core.services.reviews_import_service import ReviewsImportService
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Import reviews from external APIs (Google, TripAdvisor) into database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            choices=["google", "tripadvisor", "all"],
            default="all",
            help="Source to import from (default: all)",
        )
        parser.add_argument(
            "--max-reviews",
            type=int,
            default=50,
            help="Maximum reviews to import per source (default: 50)",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Clean up old reviews (older than 1 year)",
        )
        parser.add_argument("--verbose", action="store_true", help="Verbose output")

    def handle(self, *args, **options):
        start_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(f"🚀 Начинаем импорт отзывов в {start_time}")
        )

        # Создаем директории для команд, если их нет
        os.makedirs("backend/core/management", exist_ok=True)
        os.makedirs("backend/core/management/commands", exist_ok=True)

        # Создаем __init__.py файлы если их нет
        init_files = [
            "backend/core/management/__init__.py",
            "backend/core/management/commands/__init__.py",
        ]

        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write("# Django management commands\n")

        service = ReviewsImportService()

        try:
            # Импорт отзывов
            if options["source"] == "all":
                results = service.import_all_reviews(options["max_reviews"])
            else:
                result = service.import_from_source(
                    options["source"], options["max_reviews"]
                )
                results = {
                    "total_imported": result["imported"],
                    "total_updated": result["updated"],
                    "total_skipped": result["skipped"],
                    "sources": {options["source"]: result},
                    "errors": [],
                }

            # Выводим результаты
            self.stdout.write("📊 Результаты импорта:")
            self.stdout.write(f"   Добавлено: {results['total_imported']}")
            self.stdout.write(f"   Обновлено: {results['total_updated']}")
            self.stdout.write(f"   Пропущено: {results['total_skipped']}")

            if options["verbose"]:
                for source, data in results["sources"].items():
                    self.stdout.write(f"   {source}:")
                    self.stdout.write(f"     - добавлено: {data.get('imported', 0)}")
                    self.stdout.write(f"     - обновлено: {data.get('updated', 0)}")
                    self.stdout.write(f"     - пропущено: {data.get('skipped', 0)}")

            # Ошибки
            if results["errors"]:
                self.stdout.write(self.style.WARNING("⚠️ Ошибки:"))
                for error in results["errors"]:
                    self.stdout.write(f"   {error}")

            # Очистка старых отзывов
            if options["cleanup"]:
                deleted = service.cleanup_old_reviews()
                self.stdout.write(f"🧹 Удалено старых отзывов: {deleted}")

            # Статистика
            status = service.get_import_status()
            self.stdout.write(
                f"📈 Всего активных отзывов в БД: {status['total_reviews']}"
            )

            duration = timezone.now() - start_time
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Импорт завершен за {duration.total_seconds():.1f}s"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Ошибка импорта: {str(e)}"))
            raise
