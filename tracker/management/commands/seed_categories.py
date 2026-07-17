"""
Management command to seed a sensible set of default categories.
Run with: python manage.py seed_categories
"""
from django.core.management.base import BaseCommand
from tracker.models import Category


DEFAULT_CATEGORIES = [
    ("Salary", Category.INCOME),
    ("Freelance", Category.INCOME),
    ("Investments", Category.INCOME),
    ("Other Income", Category.INCOME),
    ("Food & Dining", Category.EXPENSE),
    ("Rent", Category.EXPENSE),
    ("Utilities", Category.EXPENSE),
    ("Transportation", Category.EXPENSE),
    ("Entertainment", Category.EXPENSE),
    ("Healthcare", Category.EXPENSE),
    ("Shopping", Category.EXPENSE),
    ("Education", Category.EXPENSE),
    ("Other Expense", Category.EXPENSE),
]


class Command(BaseCommand):
    help = "Seeds the database with a default set of income/expense categories."

    def handle(self, *args, **options):
        created_count = 0
        for name, cat_type in DEFAULT_CATEGORIES:
            _, created = Category.objects.get_or_create(name=name, type=cat_type)
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f"Done. {created_count} new categories created, "
            f"{len(DEFAULT_CATEGORIES) - created_count} already existed."
        ))
