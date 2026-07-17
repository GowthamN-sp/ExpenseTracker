"""
Admin customization for the Expense Tracker app.
"""
from django.contrib import admin
from .models import Category, Transaction, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'category', 'amount', 'date', 'created_at')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('description', 'user__username', 'category__name')
    date_hierarchy = 'date'
    ordering = ('-date',)
    autocomplete_fields = ('user', 'category')
    list_select_related = ('user', 'category')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'monthly_budget')
    search_fields = ('user__username', 'phone_number')
