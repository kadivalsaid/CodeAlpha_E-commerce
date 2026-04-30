# E-commerce Django Project

## Overview
A simple e-commerce web app built with Django. It supports product listing, product detail pages, a shopping cart, checkout flow, and user authentication.

## Features
- Product listing and detail pages
- Shopping cart and order processing
- User registration and login
- Static files (CSS/JS) and product media (images)

## Benefits
- Quick to prototype an online store using Django
- Clean project structure with separate apps (`store`, `accounts`, `ecommerce`)
- Easy to extend: add views, models, and templates as needed

## Requirements
- Python 3.8 or higher
- Django (install via `pip install django` or `pip install -r requirements.txt`)

## Setup
1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, install Django directly:

```bash
pip install django
```

3. Run migrations:

```bash
python manage.py migrate
```

4. (Optional) Create a superuser:

```bash
python manage.py createsuperuser
```

5. Collect static files (for production):

```bash
python manage.py collectstatic
```

6. Start the development server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Project layout
- `store/` — main app with models and views
- `accounts/` — user authentication and registration
- `ecommerce/` — project settings and WSGI/ASGI
- `templates/` — HTML templates
- `static/` and `media/` — CSS/JS and uploaded images

## Development tips
- Create a branch for new features.
- Add migrations and tests for database changes.

## Contributing
Create an issue or open a pull request to contribute.

## License
No license file is included. Add a `LICENSE` if you want to set terms.
