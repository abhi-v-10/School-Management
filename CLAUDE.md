# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Scholaroid is a role-based School Management System built with Django 5.2. It provides dashboards for four roles — Admin, Teacher, Student, Parent — covering classes, attendance, exams, notices, and internal messaging (including real-time chat via Django Channels).

## Common commands

Run all commands from the repo root (`manage.py` location).

```bash
# Install dependencies
pip install -r requirements.txt

# Migrations
python manage.py makemigrations
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Dev server (HTTP + autoreload)
python manage.py runserver

# Dev server via ASGI (mirrors production, needed to exercise websockets)
python -m daphne -b 127.0.0.1 -p 8000 managementProject.asgi:application

# Run tests (whole project or a single app)
python manage.py test
python manage.py test attendanceApp

# Run a single test case / method
python manage.py test attendanceApp.tests.SomeTestCase.test_something

# Collect static files (mirrors what render-build.sh does)
python manage.py collectstatic --noinput
```

There is no configured linter/formatter in this repo (no ruff/flake8/black config found) — don't assume one when making changes.

## Environment configuration

Config is read via `python-decouple` from a `.env` file (see `managementProject/settings.py`). Key variables:

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DATABASE_URL` — if unset, falls back to local `db.sqlite3` in dev; **required when `DEBUG=False`** (settings raises `ImproperlyConfigured` otherwise)
- `REDIS_URL` — optional; when set, Channels uses Redis as the channel layer, otherwise falls back to in-memory (single-process only)
- `WEBSOCKETS_ENABLED` — defaults `True`; set `False` to run HTTP-only (useful in constrained environments)
- `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` — optional Google OAuth2 login
- `CLOUDINARY_URL` (+ `CLOUDINARY_CLOUD_NAME`/`CLOUDINARY_API_KEY`/`CLOUDINARY_API_SECRET`) — optional; when set, uploaded media (profile photos, message attachments, resources) is stored on Cloudinary instead of the local filesystem via `DEFAULT_FILE_STORAGE`
- Email vars (`EMAIL_BACKEND`, `EMAIL_HOST`, etc.) — defaults to console backend in dev

## Architecture

### App layout (one Django app per domain)

- `managementProject/` — project settings, root `urls.py`, `asgi.py`/`wsgi.py`
- `accountsApp/` — custom `User` model (`AUTH_USER_MODEL`), auth (login/register/logout, Google OAuth2), role-based dashboards, `Notice` model, permission mixins
- `classesApp/` — `ClassRoom` and `Subjects` models
- `attendanceApp/` — `Attendance` records (present/absent/late), unique per `(student, date)`
- `examsApp/` — exam scheduling per class + subject
- `studentsApp/` — `Student` profile (links to `User`, `ClassRoom`, `Parent`)
- `teachersApp/` — `Teacher` profile with M2M assignment to subjects and classes
- `parentsApp/` — `Parent` profile + phone number; parent↔student linkage
- `messagingApp/` — internal user-to-user and group messaging; real-time delivery via Django Channels (`consumers.py`, `routing.py`)
- `resourcesApp/` — uploadable learning resources
- `templates/` — shared base layout (`base.html`) and global templates
- `static/` / `staticfiles/` — source static assets vs. WhiteNoise-collected output (never edit `staticfiles/` directly, it's a build artifact)
- `media/` — uploaded files (profile photos, message attachments, resources) when not using Cloudinary

### Roles and permissions

- Single-role-per-account model: `User.role` is one of `admin | teacher | student | parent` (`accountsApp/models.py`).
- Permission enforcement is done in views/templates, not Django's permission framework. The pattern is role-check mixins like `AdminRequiredMixin` in `accountsApp/mixins.py` (`UserPassesTestMixin` checking `request.user.role`), redirecting with a message on failure. Follow this same mixin pattern for new role-gated views rather than introducing a different auth mechanism.
- `AUTHENTICATION_BACKENDS` includes both Google OAuth2 (`social_core.backends.google.GoogleOAuth2`) and Django's default `ModelBackend`.

### Auth endpoints (AJAX contract)

`accounts/login/` and `accounts/register/<role>/` accept AJAX POSTs and return JSON: `{success, redirect_url}` on success or `{success: false, errors: [...]}` on failure. Non-AJAX POSTs fall back to classic redirect behavior (progressive enhancement) — preserve both paths when touching these views.

### Real-time messaging (Channels)

- `managementProject/asgi.py` builds a `ProtocolTypeRouter` with HTTP handled by Django and websockets routed through `messagingApp/routing.py`, gated by `settings.WEBSOCKETS_ENABLED`.
- `messagingApp/consumers.py` has `DirectChatConsumer` and `GroupChatConsumer`. Direct-message permission checks mirror the HTTP view logic inline in `connect()` (which role can message which — see the `allowed` checks) — keep these in sync if messaging permission rules change elsewhere.
- Channel layer backend depends on `REDIS_URL`: Redis in production/when configured, in-memory otherwise (in-memory only works with a single process/worker).

### Deployment

Targets Render.com via `render.yaml` (blueprint: web service + Postgres + optional Redis). `render-build.sh` installs deps and runs `collectstatic`; `render-start.sh` runs migrations then starts Daphne. `Procfile` also declares the Daphne process. Static files are served by WhiteNoise (`CompressedManifestStaticFilesStorage`) from `staticfiles/`. A lightweight `/healthz/` endpoint (in `managementProject/urls.py`) returns plain-text `ok` for uptime probes.
