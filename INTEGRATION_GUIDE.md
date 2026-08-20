# Cyber-Noir Security Theme — Integration Guide

**AI Phishing Detection System** — Aug 8, 2026
Status: **LIVE** — all five workspace surfaces are rendered through the new Cyber-Noir design system.

Guides you through what was added, where files live, how the routes are wired, and how to swap back to the original templates if you ever want to.

---

## 1. What changed at a glance

| Area | Before | After |
|------|--------|-------|
| Global theme | `style.css` (+ ad-hoc inline styles, Tailwind-only) | `static/css/cyber-noir-theme.css` — standalone design token system |
| Fonts | Plus Jakarta Sans + JetBrains Mono | Inter + JetBrains Mono (Cyber-Noir) |
| Background | animated gradient orbs (login) / solid dark | **Cyberpunk cityscape** `static/css/images/city.jpg` + vignette + scanline overlay |
| Cards | Tailwind glass util classes in each page | shared `.glass-card`, `.metric-card`, `.cyber-table` components |
| Login bypass | Facebook / Google `onclick → /scan` | **Unchanged — preserved exactly as-is** |
| Scanner / Scan | `/scan` | `scan_refactored.html` |
| Batch | `/batch-scan` | `batch_scan_refactored.html` |
| History | `/history` | `history_refactored.html` |
| Dashboard | `/dashboard` | `dashboard_refactored.html` |
| Signup | `/signup` | `signup_refactored.html` |

---

## 2. File placement

All new files are committed beside the originals. No original file was overwritten — every original template still exists as a fallback.

```
Phishing Detector/
├─ app.py                          ← routes now reference *_refactored.html
├─ static/css/
│   └─ cyber-noir-theme.css        ← NEW global design system
├─ static/css/images/
│   └─ city.jpg                    ← the cyberpunk cityscape background
│
├─ templates/
│   ├─ index.html                  ← LOGIN: untouched (bypass preserved)
│   ├─ scan_refactored.html        ← NEW scanner (hero + VirusTotal + details modal)
│   ├─ batch_scan_refactored.html  ← NEW batch scanner
│   ├─ history_refactored.html     ← NEW scan history table
│   ├─ dashboard_refactored.html   ← NEW analytics dashboard
│   └─ signup_refactored.html      ← NEW create-account page
│
│   # originals still present as fallback:
│   ├─ scan.html  batch_scan.html  history.html  dashboard.html  signup.html
```

---

## 3. How the routes are wired (app.py)

Each `render_template(...)` call now points at the refactored template. If you ever want the **original** look back, just change the string back to the non-`_refactored` filename — no other edit needed.

| Route | render_template(...) |
|-------|----------------------|
| `login` (`/`) | `index.html` *(kept — bypass login)* |
| `signup` (`/signup`) | `signup_refactored.html` |
| `scan` (`/scan`) ×2 | `scan_refactored.html` |
| `history` (`/history`) | `history_refactored.html` |
| `batch_scan` (`/batch-scan`) | `batch_scan_refactored.html` |
| `dashboard` (`/dashboard`) | `dashboard_refactored.html` |

Context variables are **identical** to the originals — `form`, `predict`, `url`, `confidence`, `vt_result`, `malicious`, `suspicious`, `harmless`, `vendors`, `scans`, `total_scans`, `phishing_count`, `safe_count`, `recent_scans`, `results`. No backend logic changed.

---

## 4. Bypass login — exactly how you want it (OPEN ACCESS)

`templates/index.html` is **completely untouched**. Both social buttons redirect straight to the scanner with no auth:

```html
<!-- Continue with Facebook -->
<button onclick="window.location.href='/scan'">…</button>
<!-- Continue with Google -->
<button onclick="window.location.href='/scan'">…</button>
```

Click either button → `/scan` → start scanning immediately. **The bypass now truly works from a cold start** — `/scan`, `/batch-scan`, `/history`, and `/dashboard` no longer block anonymous visitors (previously `@require_auth` bounced visitors back to login, which silently broke the bypass). Secure pages run in an open/resumer consumer mode:

- Anonymous scans still save to the database (`user_id` is `NULL`) and return full results.
- Anonymous visitors see an **empty** personal History / Dashboard (auto counts of 0) — no data leak.
- The email form + admin login still work as before (admin@ssipmt.com / Admin@123).
- The JSON API (`/api/scan`) is the one thing kept `@require_auth` — it answers 401 with an auth hint for signed-out callers.

To go back to forced-login-only, re-add the `@require_auth` decorator lines removed in `app.py` (the originals are commented/visible in git history).

---

## 5. New dependencies

- **Fonts** — loaded via Google Fonts CDN (embedded in `cyber-noir-theme.css` with `@import`):
  - `Inter` (UI) and `JetBrains Mono` (data / URLs / code)
- **Tailwind CSS CDN** — added to each refactored template head for the layout/utility classes. No build step, no `tailwind.config`.
- **Material Symbols** — icon font, loaded by CDN in the refactored heads.
- **Cityscape** — must exist at `static/css/images/city.jpg` (flask serves it from the `static/` root; the CSS references it as `../css/images/city.jpg ` — relative to the stylesheet at `static/css/`). If you add a different image, drop it there with the same filename.

> The theme class is `.glass-card`, `.glass-card-elevated`, `.glass-card-transparent`, `.btn .btn-primary/-secondary/-ghost`, `.input`, `.textarea`, `.cyber-table`, `.metric-card`, `.status-badge(-safe/-danger/-warning/-pending)`, `.page-enter`, `.neon-text-cyan/-pink`. See the CSS file for the full token list (`--neon-cyan`, `--surface-card`, `--glow-cyan`, …).

---

## 6. Page-reveal animation (why there's a tiny script)

`cyber-noir-theme.css` defines `.page-enter` as `opacity: 0; translateY(20px)` and transitions in when `.page-enter-active` is added. Each refactored page includes a small loader that adds that class on load and honors the inline `animation-delay` for a staggered cascade:

```js
document.querySelectorAll('.page-enter').forEach(el => {
  el.style.transitionDelay = getComputedStyle(el).animationDelay || '0s';
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('page-enter-active')));
});
```

This is what produces the fade-in + slide-up, staggered entrance.

---

## 7. Accessibility & performance

- **Reduced motion**: the theme disables animations/transitions under `@media (prefers-reduced-motion: reduce)`.
- **Focus visibility**: global `:focus-visible` cyan outline.
- **GPU-friendly**: animations use `transform` / `opacity` only; `.gpu-accelerated` utility adds `translateZ(0)` + `will-change`.
- **Custom scrollbars** on the history table / vendor list.

---

## 8. Rollback (one minute)

To restore the original look entirely, edit `app.py` and revert each `render_template("…. _refactored.html")` to the plain name. The original templates were never modified, so this is a full one-line-per-route undo.

---

## 9. Verify

Start the app:

```bash
python app.py
```

- `http://localhost:5000` → login with bypass buttons.
- Click **Continue with Google** → scanner (`/scan`).
- Submit a URL → Result + VirusTotal card + **More Info** modal + PDF/CSV export.
- `/batch-scan`, `/history`, `/dashboard`, `/signup` → all Cyber-Noir.

---

**Summary:** Login bypass preserved · Scanner / Batch / History / Dashboard / Signup fully restyled to a cohesive Cyber-Noir security theme · Originals kept as fallback.