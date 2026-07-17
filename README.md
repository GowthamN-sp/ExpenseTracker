# 💰 Expense Tracker — Django Web Application

A full-stack personal finance web app built with Django, where users can register, log in, and
track their income and expenses with a modern dashboard, interactive Chart.js visualizations,
monthly reports, and CSV export.

---

## 📖 Project Overview

Expense Tracker is a portfolio-ready, production-structured Django application that demonstrates
authentication, per-user data isolation, class-based views, Django ORM aggregation, and a
responsive Bootstrap 5 UI. Every user only ever sees their own transactions — categories are
shared, but income/expense records are scoped to the logged-in user at the queryset level.

---

## ✨ Features

### Authentication
- User registration, login, logout
- "Remember Me" login option (extends session to 2 weeks)
- Editable profile page (name, email, phone, bio, monthly budget)
- Change password flow

### Transactions
- Add / Edit / Delete / View income & expense transactions
- Server-side validation (positive amounts only, category must match transaction type)
- AJAX delete confirmation modal on the transaction list
- Pagination (10 per page)

### Filters & Search
- Filter by category, transaction type, month, and date range
- Free-text search across description and category name

### Dashboard
- Summary cards: Total Income, Total Expense, Current Balance, Number of Transactions
- Recent transactions table
- 4 live Chart.js charts:
  - Pie — Expense by Category
  - Doughnut — Income vs Expense
  - Bar — Monthly Income vs Monthly Expense
  - Line — Expense Trend (last 6 months)

### Reports & Analytics
- Monthly report with income, expense, savings, and transaction count
- Category breakdown table for the selected month
- Export the monthly report to CSV
- Built entirely on Django ORM aggregation (`Sum`, `Count`, `Annotate`, `Aggregate`, `TruncMonth`)

### Admin Panel
- Custom `ModelAdmin` for Category, Transaction, and Profile
- List filters, search fields, date hierarchy, and autocomplete on Transaction

### UI / UX
- Responsive Bootstrap 5 layout with a collapsible sidebar (mobile-friendly)
- Bootstrap Icons throughout
- Dark mode toggle (persisted via cookie)
- Card hover effects and fade-in animations
- Empty-state illustrations for no-data views
- Loading spinner overlay on form submission
- Django messages framework wired to Bootstrap alert styles

---

## 🛠️ Technologies Used

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Backend        | Django (Class-Based Views, ORM)      |
| Database       | SQLite                               |
| Frontend       | HTML5, CSS3, Bootstrap 5             |
| Charts         | Chart.js                             |
| Icons          | Bootstrap Icons                      |
| Auth           | Django built-in authentication       |

---

## 🚀 Installation Steps

```bash
# 1. Clone / unzip the project and enter the folder
cd expense_tracker

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 5. (Recommended) seed a default set of categories
python manage.py seed_categories

# 6. Create an admin account
python manage.py createsuperuser

# 7. Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — you'll be redirected to the login page. Register a new account
or log in with your superuser, then head to the dashboard.

The Django admin is available at `http://127.0.0.1:8000/admin/`.

---

## 📸 Screenshots

> Replace these placeholders with real screenshots once you've run the app locally.

| Dashboard | Transactions | Monthly Report |
|-----------|--------------|-----------------|
| `212838.png` | `212816.png` | `212729.png` |

---

## 📁 Folder Structure

```
expense_tracker/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── expense_tracker/            # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── tracker/                    # Main application
│   ├── models.py                # Category, Transaction, Profile
│   ├── views.py                 # Class-based + function-based views
│   ├── forms.py                 # ModelForms + custom validation
│   ├── urls.py                  # App-level URL routing
│   ├── admin.py                 # Customized admin
│   ├── signals.py               # Auto-create Profile on user creation
│   ├── management/
│   │   └── commands/
│   │       └── seed_categories.py
│   └── migrations/
│
├── templates/
│   ├── base.html
│   ├── navbar.html               # Sidebar navigation
│   ├── _messages.html
│   ├── registration/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── password_change.html
│   │   └── password_change_done.html
│   └── tracker/
│       ├── dashboard.html
│       ├── transaction_list.html
│       ├── transaction_form.html
│       ├── transaction_detail.html
│       ├── transaction_confirm_delete.html
│       ├── profile.html
│       └── monthly_report.html
│
└── static/
    ├── css/style.css
    └── js/script.js
```

---

## 🔗 URL Map

| URL                              | View                    |
|-----------------------------------|-------------------------|
| `/`                                | Dashboard (redirects to login if anonymous) |
| `/dashboard/`                      | Dashboard |
| `/transactions/`                   | Transaction list (filters + search + pagination) |
| `/transactions/add/`               | Add transaction |
| `/transactions/edit/<id>/`         | Edit transaction |
| `/transactions/delete/<id>/`       | Delete transaction |
| `/transactions/<id>/`              | Transaction detail |
| `/reports/`                        | Monthly report |
| `/reports/export/`                 | Export monthly report as CSV |
| `/login/` `/logout/` `/register/`  | Authentication |
| `/profile/`                        | Profile view/edit |
| `/admin/`                          | Django admin |

---

## 🔮 Future Improvements

- Multi-currency support
- Recurring transactions (subscriptions, rent, salary)
- Budget alerts when a category approaches its monthly limit
- REST API (Django REST Framework) for a mobile client
- Data export to PDF in addition to CSV
- Per-user custom categories with icons/colors
- Bank statement import (CSV/OFX parsing)

---

## 📄 License

This project is provided as a learning/portfolio resource. Feel free to fork and adapt it.
