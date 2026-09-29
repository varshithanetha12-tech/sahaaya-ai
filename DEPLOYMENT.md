# Sahaaya AI — Production Web Deployment & Mobile PWA Guide

This guide provides step-by-step instructions to deploy the **Sahaaya AI** Real-Time Stress and Trauma Assessment Platform to the web and configure it as an installable Progressive Web App (PWA) on smartphones (Android & iOS).

---

## 1. Architecture Overview

Sahaaya AI is architected as a lightweight, production-ready full-stack application:

* **Backend Engine:** FastAPI (Python 3.10+ / 3.12) running asynchronous REST endpoints, multilingual Indic NLP evaluation, speech prosody modeling, and Stress Vulnerability Index (SVI) calculation.
* **Frontend:** Responsive Single-Page Application (SPA) with Tailwind CSS, Chart.js, and vanilla JavaScript.
* **Mobile & PWA:** Installable Progressive Web App with Web App Manifest, Service Worker offline caching, responsive touch targets, mobile navigation drawer, and bottom navigation bar.
* **Database & Persistence:** Production JSON state persistence (`db_state.json`) with automated seeding and zero external database dependencies needed for hackathon evaluation.

Because FastAPI serves the static frontend directly from `/static` and `index.html` from `/`, **a single unified service deployment (Render, Railway, or Docker)** is the simplest, fastest, and most robust deployment option. A decoupled deployment (Vercel frontend + Render backend) is also supported.

---

## 2. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for the HTTP server to listen on. Render and Railway inject this automatically. |
| `HOST` | `0.0.0.0` | Host IP address to bind (`0.0.0.0` for public web containers). |
| `ENV` | `production` | Set to `production` to disable auto-reload and secure headers. Set to `development` for local testing. |
| `CORS_ORIGINS` | `*` | Comma-separated list of allowed frontend origins (e.g. `https://sahaaya.vercel.app`). Use `*` for open prototype access. |
| `DATA_DIR` | `app/static/data` | Directory where database state is persisted to disk across restarts. |

---

## 3. Local Production Build & Testing

To test the production build on your local machine:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run in production mode:**
   ```bash
   python run.py
   ```
   * Access URL: `http://localhost:8000/` or `http://127.0.0.1:8000/`
   * Health Check: `http://localhost:8000/health`
   * Interactive API Documentation (Swagger): `http://localhost:8000/docs`

3. **Execute automated integration test suite:**
   ```bash
   python test_system.py
   ```

---

## 4. Option A: 1-Click Deployment to Render (Recommended)

Render offers a free tier suitable for hackathons with automatic HTTPS and Git integration.

### Method 1: Connecting your GitHub Repository
1. Push your repository to **GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** → **Web Service**.
4. Connect your GitHub repository.
5. Configure the following fields:
   * **Name:** `sahaaya-ai`
   * **Region:** Any (e.g. *Oregon (US West)* or *Frankfurt (EU)*)
   * **Branch:** `master` (or `main`)
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `python run.py`
   * **Instance Type:** `Free`
6. Under **Advanced** → **Environment Variables**, add:
   * `ENV` = `production`
   * `CORS_ORIGINS` = `*`
7. Click **Create Web Service**.
8. Within 2–3 minutes, Render builds the container and provides your live public URL:
   `https://sahaaya-ai.onrender.com`

---

## 5. Option B: Deployment to Railway.app

1. Log in to [Railway.app](https://railway.app/).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your Sahaaya AI repository.
4. Railway will automatically detect the Python environment and `requirements.txt`.
5. Under **Settings** → **Networking**, click **Generate Domain** to get a public URL (e.g., `https://sahaaya-ai.up.railway.app`).
6. Under **Variables**, add:
   * `ENV` = `production`
   * `HOST` = `0.0.0.0`
7. Deployment completes automatically.

---

## 6. Option C: Docker Deployment (Any Cloud / VPS / HuggingFace)

A production-hardened `Dockerfile` is included in the project root.

1. **Build the container image:**
   ```bash
   docker build -t sahaaya-ai:latest .
   ```

2. **Run the container locally or on a server:**
   ```bash
   docker run -d -p 8000:8000 -e ENV=production -e PORT=8000 --name sahaaya-app sahaaya-ai:latest
   ```

3. **Verify running container:**
   ```bash
   curl http://localhost:8000/health
   ```

You can deploy this Docker container directly to **Google Cloud Run**, **AWS App Runner**, **Fly.io**, or **DigitalOcean App Platform**.

---

## 7. Option D: Decoupled Deployment (Frontend on Vercel + Backend on Render)

If your team prefers hosting the static frontend on Vercel and the API on Render:

1. **Deploy Backend to Render** as described in Section 4. Note your backend URL (e.g., `https://sahaaya-ai.onrender.com`).
2. **Deploy Frontend to Vercel:**
   * Import the repository on [Vercel](https://vercel.com/).
   * Select root directory.
   * `vercel.json` will automatically configure routing.
3. **Configure Backend CORS:**
   * In your Render service environment variables, set:
     `CORS_ORIGINS=https://your-vercel-domain.vercel.app`

---

## 8. Mobile PWA & "Add to Home Screen" Setup

Sahaaya AI is fully configured as an installable Progressive Web App.

### On Android (Chrome / Edge / Firefox):
1. Open the public web URL in Chrome on your phone.
2. An automatic banner will appear: **"Add Sahaaya AI to Home Screen"**.
3. Alternatively, tap the browser menu (⋮) → tap **"Install App"** or **"Add to Home Screen"**.
4. The Sahaaya AI icon with the teal shield will be added to your app drawer and home screen.
5. When launched, it runs in fullscreen standalone mode without browser navigation bars.

### On iPhone / iPad (Safari):
1. Open the public web URL in **Safari**.
2. Tap the **Share** button (box with an upward arrow at the bottom).
3. Scroll down and tap **"Add to Home Screen"**.
4. Confirm the name: **Sahaaya AI**.
5. Tap **Add** in the top right corner.
6. The app opens like a native iOS application with full safe-area notch and home indicator support.

---

## 9. Mobile Responsive Layout Checklist

The interface adapts smoothly across all screen resolutions:
* **320px – 375px (iPhone SE, smaller Androids):** Single-column stacked cards, compact touch buttons, simplified header with hamburger navigation and bottom navigation bar.
* **390px – 414px (iPhone 13/14/15/Plus, Galaxy S):** Full conversational assessment view, live prosody gauges, and responsive result cards.
* **768px (iPad, Android tablets):** Two-column KPI grids, side-by-side radar and speech charts.
* **1024px – 1440px+ (Laptops & Desktops):** Full horizontal navigation, 12-column officer triage table, and multi-pane case dossiers.

---

## 10. Database Persistence & Resetting Demo Data

* **Persistent State:** All complaints, conversational turns, referrals, high-risk alert acknowledgments, and follow-ups are automatically persisted to `app/static/data/db_state.json`.
* **Safe Reset:** To restore the original 10 synthetic evaluation cases (e.g. between hackathon presentation rounds), authorized officers or administrators can:
  * In the UI: Go to **Admin** → Click **Reset Demo Data**.
  * Via API: Call `POST /api/admin/reset-demo-data`.

---

## 11. Updating & Redeploying

When pushing new updates:
1. Commit changes to git:
   ```bash
   git add .
   git commit -m "update: improvements"
   git push origin master
   ```
2. Render / Railway will automatically detect the push, rebuild, and perform a zero-downtime rolling deployment.
