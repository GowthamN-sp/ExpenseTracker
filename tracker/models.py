"""
Models for the Expense Tracker application.

Category      -> A label used to classify transactions (e.g. Salary, Rent, Food).
Transaction   -> A single income or expense record belonging to a user.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.urls import reverse


class Category(models.Model):
    """A category used to classify a transaction as Income or Expense."""

    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=EXPENSE)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        unique_together = ('name', 'type')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    """A single income or expense transaction belonging to a specific user."""

    INCOME = 'income'
    EXPENSE = 'expense'
    TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Amount must be greater than zero.")]
    )
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=EXPENSE)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} on {self.date}"

    def get_absolute_url(self):
        return reverse('transaction-detail', kwargs={'pk': self.pk})

    @property
    def signed_amount(self):
        """Returns amount as negative for expenses, positive for income (useful for charts/reports)."""
        return self.amount if self.transaction_type == self.INCOME else -self.amount


class Profile(models.Model):
    """Extra profile information for a user, created automatically via signal."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, blank=True)
    bio = models.CharField(max_length=255, blank=True)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Profile of {self.user.username}"
