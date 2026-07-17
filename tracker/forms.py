"""
Forms for the Expense Tracker application.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Transaction, Category, Profile


class BootstrapPasswordChangeForm(PasswordChangeForm):
    """PasswordChangeForm with Bootstrap styling applied to every field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class RegisterForm(UserCreationForm):
    """Extended user registration form that also captures an email address."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginRememberForm(forms.Form):
    """Small helper mixin field group added on top of AuthenticationForm in the view/template."""
    remember_me = forms.BooleanField(required=False, initial=True)


class TransactionForm(forms.ModelForm):
    """Form used to create and edit Transaction records."""

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'amount', 'description', 'date']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_transaction_type'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional note'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        # Ensure the chosen category matches the chosen transaction type
        if transaction_type and category and category.type != transaction_type:
            self.add_error('category', 'Selected category does not match the transaction type.')
        return cleaned_data


class CategoryForm(forms.ModelForm):
    """Form used to quickly add a new category (e.g. from the transaction form)."""

    class Meta:
        model = Category
        fields = ['name', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }


class ProfileForm(forms.ModelForm):
    """Form used to edit extended profile information."""

    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['phone_number', 'bio', 'monthly_budget']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['first_name', 'last_name', 'email']:
            self.fields[name].widget.attrs['class'] = 'form-control'
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data.get('first_name', '')
        profile.user.last_name = self.cleaned_data.get('last_name', '')
        profile.user.email = self.cleaned_data.get('email', '')
        if commit:
            profile.user.save()
            profile.save()
        return profile


class TransactionFilterForm(forms.Form):
    """Non-model form used purely to render/validate the filter bar on the transaction list page."""

    search = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search description...'}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'}))
    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Transaction.TYPE_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select'}))
    month = forms.ChoiceField(
        required=False,
        choices=[('', 'All Months')] + [(str(i), name) for i, name in enumerate(
            ['January', 'February', 'March', 'April', 'May', 'June',
             'July', 'August', 'September', 'October', 'November', 'December'], start=1)],
        widget=forms.Select(attrs={'class': 'form-select'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))
