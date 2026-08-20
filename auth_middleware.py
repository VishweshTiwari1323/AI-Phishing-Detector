"""Enhanced Security Middleware & Authentication Guards."""

from functools import wraps
import time
from flask import current_app, jsonify, redirect, request, session, url_for
from flask_login import current_user, logout_user


def _is_api_request():
    """Helper to detect whether incoming request expects JSON/API handling."""
    return (
        request.is_json
        or request.path.startswith("/api/")
        or request.headers.get("Accept") == "application/json"
    )


def require_auth(f):
    """Authentication decorator with API/JSON awareness and redirect tracking."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if _is_api_request():
                return (
                    jsonify(
                        {
                            "error": "Authentication required",
                            "redirect": url_for("login_page"),
                        }
                    ),
                    401,
                )

            # Preserve the attempted path for post-login redirect
            return redirect(url_for("login_page", next=request.path))

        # Track user activity timestamp
        session["last_activity"] = time.time()
        return f(*args, **kwargs)

    return decorated_function


def guest_only(f):
    """Restricts access to unauthenticated users only (login, signup)."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


def check_session_timeout(app, timeout_minutes=30):
    """Enforces inactivity timeouts on authenticated sessions."""

    @app.before_request
    def enforce_timeout():
        if current_user.is_authenticated:
            last_activity = session.get("last_activity")

            if last_activity:
                elapsed = time.time() - last_activity

                if elapsed > (timeout_minutes * 60):
                    logout_user()
                    session.clear()

                    if _is_api_request():
                        return (
                            jsonify(
                                {
                                    "error": "Session timed out due to inactivity",
                                    "redirect": url_for("login_page"),
                                }
                            ),
                            401,
                        )

                    return redirect(url_for("login_page", timeout="true"))

            # Update rolling activity timestamp
            session["last_activity"] = time.time()


def validate_session_integrity(app):
    """Ensures active user account integrity on each incoming request."""

    @app.before_request
    def validate_session():
        # Safely skip unmapped routes, static files, and public endpoints
        endpoint = request.endpoint or ""
        if endpoint in ["static", "login", "signup"] or endpoint.startswith(
            "static."
        ):
            return

        if current_user.is_authenticated:
            # Check if user account remains valid and active
            if not getattr(current_user, "is_active", True):
                logout_user()
                session.clear()

                if _is_api_request():
                    return (
                        jsonify(
                            {
                                "error": "Account disabled or invalid session",
                                "redirect": url_for("login_page"),
                            }
                        ),
                        401,
                    )

                return redirect(url_for("login_page", session_invalid="true"))


def setup_security_headers(app):
    """Attaches standard security and hardening headers to all HTTP responses."""

    @app.after_request
    def set_security_headers(response):
        # Clickjacking mitigation
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # MIME sniffing prevention
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer metadata protection
        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )

        # XSS filtering configuration
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HTTP Strict Transport Security (HSTS in production / non-debug)
        is_production = (
            not app.debug and app.config.get("ENV") == "production"
        ) or app.config.get("SESSION_COOKIE_SECURE", False)

        if is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Content Security Policy (CSP)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )

        return response