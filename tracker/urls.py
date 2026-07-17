"""
URL configuration for the tracker app.
"""
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView
from . import views

urlpatterns = [
    # Redirect root -> dashboard (dashboard itself requires login and will
    # bounce anonymous users to the login page).
    path('', views.DashboardView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/add/', views.TransactionCreateView.as_view(), name='transaction-add'),
    path('transactions/edit/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction-edit'),
    path('transactions/delete/<int:pk>/', views.TransactionDeleteView.as_view(), name='transaction-delete'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),

    # Reports
    path('reports/', views.MonthlyReportView.as_view(), name='monthly-report'),
    path('reports/export/', views.export_monthly_report_csv, name='export-report-csv'),

    # Auth
    path('login/', views.RememberMeLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/password/', PasswordChangeView.as_view(
        template_name='registration/password_change.html',
        form_class=views.BootstrapPasswordChangeForm,
        success_url='/profile/password/done/'
    ), name='password_change'),
    path('profile/password/done/', PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
]
