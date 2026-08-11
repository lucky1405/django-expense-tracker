# django-expense-tracker

A full-stack personal expense management application built with Django and Bootstrap 5. Users can securely manage income and expenses, create custom categories, set monthly budgets, and track their finances through an interactive dashboard with spending analytics.

## Setup

```bash
git clone https://github.com/lucky1405/django-expense-tracker.git
cd expense_tracker

python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt

Create a .env file in the project root:

SECRET_KEY=your-secret-key
DEBUG=True

Run database migrations:

python manage.py migrate
```

## Run

```bash
python manage.py runserver

Open http://127.0.0.1:8000/ in your browser.

To create an admin account:

python manage.py createsuperuser
```

## Tests

```bash
python manage.py test
```
