# ApartHub — Intelligent Smart Apartment Platform

ApartHub is a Django rental platform for advertising, discovering, recommending and managing residential apartments in Yola/Jimeta, Adamawa State. Its visual layer is a Django-native adaptation of the Apart real-estate template: a prominent home search, property-card grid, feature blocks, and warm teal/orange design system—not a static prototype.

## Implemented features

- Tenant and landlord/agent registration with a custom email-based user model.
- Private preferences and a content-based recommendation service.
- Verification document submissions and a verified-owner gate before listing submission.
- Listing management, multiple images, moderated statuses, search and filters.
- Favourites, interaction logging, apartment-scoped messages and inspection bookings.
- In-app notifications, tenant reports and role-aware dashboards.
- Django Admin back-office configuration for verification, listing moderation and platform management.

## Technology

- Python 3, Django, Django ORM, forms and authentication
- Bootstrap 5, Bootstrap Icons and responsive custom CSS
- SQLite development support and PostgreSQL-compatible configuration
- scikit-learn / pandas for recommendation features

## Quick start (Windows)

```powershell
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Use `/admin/` for verification and listing moderation actions.

## Environment

Copy `.env.example` to `.env` and set `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, and `ALLOWED_HOSTS`. PostgreSQL is supported with a URL such as:

```text
DATABASE_URL=postgresql://aparthub:password@localhost:5432/aparthub
```

Never commit `.env` or SMTP credentials.

## Recommendation engine

`apartments/services.py` exposes `recommend_apartments(tenant, limit=10)`. It retrieves only available apartments; creates TF-IDF features from location and amenities; uses MinMax scaling for price and bedroom count; combines the features; ranks by cosine similarity; and returns 0–100 match scores plus readable match reasons. A deterministic fallback exists only for incomplete local installations; production should install the declared requirements.

Views, saves, messages and booking requests are recorded in `InteractionLog`, leaving room for a future hybrid recommendation model without exposing tenant preferences to owners.

## Roles

| Role | Main capabilities |
| --- | --- |
| Tenant | Search, private preferences, recommendations, saves, messages, inspection requests and reports |
| Landlord / Agent | Verification, own listings after approval, messages and booking responses |
| Administrator | Verification and listing moderation, user oversight and activity monitoring |

Backend permission checks guard private resources; navigation visibility is only a convenience.

## Checks and tests

```powershell
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py test
```

The included tests cover tenant registration and recommendation exclusion of unavailable listings. Add coverage for each new workflow before deployment.

## Project layout

```text
config/            Environment-based Django settings
accounts/          Users, preferences and owner verification
apartments/        Listings, images, saves, search and recommendation service
bookings/          Inspection requests and responses
messaging/         Apartment-scoped conversations
notifications/     In-app notification model and service
moderation/        Tenant listing reports
dashboard/         Role-aware dashboard views
templates/         Reusable Bootstrap templates
static/css/         Apart-inspired visual system
```

## Production deployment

Use `config.settings.production`, PostgreSQL, a real email backend, HTTPS, a strong environment-only secret key, configured allowed hosts, and managed static/media storage. Review upload-storage policies before release.
