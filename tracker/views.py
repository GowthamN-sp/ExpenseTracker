"""
Views for the Expense Tracker application.

Class-based views are used wherever Django provides a good generic fit
(ListView, CreateView, UpdateView, DeleteView, DetailView). Function-based
views are used for registration and the small profile/report helpers where
a CBV would add more boilerplate than it removes.
"""
import csv
import json
from calendar import month_name
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)

from .forms import (
    RegisterForm, TransactionForm, ProfileForm, TransactionFilterForm,
    BootstrapPasswordChangeForm,
)
from .models import Transaction, Category, Profile


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

class RememberMeLoginView(LoginView):
    """Login view that supports a 'Remember Me' checkbox controlling session expiry."""
    template_name = 'registration/login.html'

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        response = super().form_valid(form)
        if remember_me:
            # Keep the session alive for 2 weeks
            self.request.session.set_expiry(1209600)
        else:
            # Expire the session when the browser closes
            self.request.session.set_expiry(0)
        return response


def register_view(request):
    """Handles new user sign-up."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome aboard, {user.username}! Your account has been created.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile_view(request):
    """Displays and updates the logged-in user's profile."""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile)

    stats = Transaction.objects.filter(user=request.user).aggregate(
        total_transactions=Count('id'),
        total_income=Sum('amount', filter=Q(transaction_type=Transaction.INCOME)),
        total_expense=Sum('amount', filter=Q(transaction_type=Transaction.EXPENSE)),
    )
    return render(request, 'tracker/profile.html', {'form': form, 'profile': profile, 'stats': stats})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user_transactions(user):
    """Every user should only ever see their own transactions."""
    return Transaction.objects.filter(user=user).select_related('category')


def _apply_filters(queryset, request):
    """Applies GET-parameter filters (search, category, type, month, date range)."""
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    transaction_type = request.GET.get('transaction_type', '')
    month = request.GET.get('month', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if search:
        queryset = queryset.filter(
            Q(description__icontains=search) | Q(category__name__icontains=search)
        )
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if transaction_type:
        queryset = queryset.filter(transaction_type=transaction_type)
    if month:
        queryset = queryset.filter(date__month=month)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    return queryset


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    """Main landing page after login: summary cards, recent transactions, chart data."""
    template_name = 'tracker/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        qs = _user_transactions(user)

        # --- Summary cards (Sum / Count / Aggregate) ---
        totals = qs.aggregate(
            total_income=Sum('amount', filter=Q(transaction_type=Transaction.INCOME)),
            total_expense=Sum('amount', filter=Q(transaction_type=Transaction.EXPENSE)),
            total_transactions=Count('id'),
        )
        total_income = totals['total_income'] or Decimal('0')
        total_expense = totals['total_expense'] or Decimal('0')
        context['total_income'] = total_income
        context['total_expense'] = total_expense
        context['balance'] = total_income - total_expense
        context['total_transactions'] = totals['total_transactions']

        # --- Recent transactions table ---
        context['recent_transactions'] = qs[:8]

        # --- Pie chart: Expense by Category (Annotate + Aggregate) ---
        expense_by_category = (
            qs.filter(transaction_type=Transaction.EXPENSE)
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        context['expense_pie_labels'] = json.dumps([c['category__name'] for c in expense_by_category])
        context['expense_pie_data'] = json.dumps([float(c['total']) for c in expense_by_category])

        # --- Doughnut chart: Income vs Expense ---
        context['income_vs_expense_data'] = json.dumps([float(total_income), float(total_expense)])

        # --- Bar chart: Monthly Income vs Monthly Expense (last 6 months, Annotate by TruncMonth) ---
        monthly_qs = (
            qs.annotate(month=TruncMonth('date'))
            .values('month', 'transaction_type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        monthly_map = {}
        for row in monthly_qs:
            if row['month'] is None:
                continue
            key = row['month'].strftime('%Y-%m')
            monthly_map.setdefault(key, {'income': 0, 'expense': 0})
            monthly_map[key][row['transaction_type']] = float(row['total'])

        sorted_months = sorted(monthly_map.keys())[-6:]
        context['bar_labels'] = json.dumps(sorted_months)
        context['bar_income_data'] = json.dumps([monthly_map[m]['income'] for m in sorted_months])
        context['bar_expense_data'] = json.dumps([monthly_map[m]['expense'] for m in sorted_months])

        # --- Line chart: Expense trend over the same months ---
        context['line_labels'] = context['bar_labels']
        context['line_expense_data'] = context['bar_expense_data']

        return context


# ---------------------------------------------------------------------------
# Transaction CRUD
# ---------------------------------------------------------------------------

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'tracker/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        qs = _user_transactions(self.request.user)
        return _apply_filters(qs, self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TransactionFilterForm(self.request.GET or None)
        # Preserve query string across pagination links
        get_params = self.request.GET.copy()
        get_params.pop('page', None)
        context['querystring'] = get_params.urlencode()
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'tracker/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def get_initial(self):
        initial = super().get_initial()
        t_type = self.request.GET.get('type')
        if t_type in (Transaction.INCOME, Transaction.EXPENSE):
            initial['transaction_type'] = t_type
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Transaction added successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Transaction'
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'tracker/transaction_form.html'
    success_url = reverse_lazy('transaction-list')

    def get_queryset(self):
        # Users may only edit their own transactions
        return _user_transactions(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Transaction updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Transaction'
        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('transaction-list')
    template_name = 'tracker/transaction_confirm_delete.html'

    def get_queryset(self):
        return _user_transactions(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Transaction deleted.")
        return super().form_valid(form)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'tracker/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return _user_transactions(self.request.user)


# ---------------------------------------------------------------------------
# Monthly Report
# ---------------------------------------------------------------------------

class MonthlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/monthly_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        year = int(self.request.GET.get('year', today.year))
        month = int(self.request.GET.get('month', today.month))

        qs = _user_transactions(self.request.user).filter(date__year=year, date__month=month)
        totals = qs.aggregate(
            total_income=Sum('amount', filter=Q(transaction_type=Transaction.INCOME)),
            total_expense=Sum('amount', filter=Q(transaction_type=Transaction.EXPENSE)),
            total_transactions=Count('id'),
        )
        total_income = totals['total_income'] or Decimal('0')
        total_expense = totals['total_expense'] or Decimal('0')

        by_category = (
            qs.values('category__name', 'transaction_type')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('-total')
        )

        context.update({
            'year': year,
            'month': month,
            'month_name': month_name[month],
            'total_income': total_income,
            'total_expense': total_expense,
            'savings': total_income - total_expense,
            'total_transactions': totals['total_transactions'],
            'by_category': by_category,
            'transactions': qs,
            'years': range(today.year - 5, today.year + 1),
            'months': list(enumerate(month_name))[1:],
        })
        return context


@login_required
def export_monthly_report_csv(request):
    """Exports the current month's (or requested month's) transactions to CSV."""
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    qs = _user_transactions(request.user).filter(date__year=year, date__month=month)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{year}_{month:02d}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount'])
    for t in qs:
        writer.writerow([t.date, t.get_transaction_type_display(), t.category.name, t.description, t.amount])

    totals = qs.aggregate(
        total_income=Sum('amount', filter=Q(transaction_type=Transaction.INCOME)),
        total_expense=Sum('amount', filter=Q(transaction_type=Transaction.EXPENSE)),
    )
    total_income = totals['total_income'] or Decimal('0')
    total_expense = totals['total_expense'] or Decimal('0')
    writer.writerow([])
    writer.writerow(['Total Income', '', '', '', total_income])
    writer.writerow(['Total Expense', '', '', '', total_expense])
    writer.writerow(['Savings', '', '', '', total_income - total_expense])

    return response
