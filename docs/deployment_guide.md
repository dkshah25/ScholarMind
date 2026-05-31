# ScholarMind Cloud Deployment Guide

This guide outlines the steps to deploy **ScholarMind** to production. Since standard cloud hosting instances (like Render or Railway) are stateless and ephemeral, we utilize our **Zero-Config Supabase sync engine** to persist session and paper data, and deploy the frontend to **Vercel**.

---

## 🏗️ Deployment Architecture

```
  [ Next.js Frontend ] (Deployed on Vercel)
          │
          ▼ (HTTPS API requests)
  [ FastAPI Backend ] (Deployed on Render / Railway)
      │         │
      │         ▼
      │   [ Gemini API ] (Generative AI & text-embedding-004)
      │
      ▼ (Direct HTTP REST synchronization)
  [ Supabase DB ] (Persistent Session Storage)
```

---

## 1. Database Setup (Supabase)

Because cloud server disks reset during redeploys, we must activate Supabase synchronization to store session records.

1. Go to **[Supabase](https://supabase.com/)** and create a free project.
2. In your Supabase Dashboard, navigate to the **SQL Editor** and execute the following queries to establish the database schema:

```sql
-- 1. Create the research_sessions table
CREATE TABLE research_sessions (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    papers TEXT DEFAULT '[]',
    gaps TEXT DEFAULT '[]',
    hypotheses TEXT DEFAULT '[]',
    experiments TEXT DEFAULT '[]',
    reports TEXT DEFAULT '{}',
    contradictions TEXT DEFAULT '[]',
    trends TEXT DEFAULT '{}',
    copilot_history TEXT DEFAULT '[]',
    benchmarks TEXT DEFAULT '{}',
    patents TEXT DEFAULT '[]',
    debate_transcript TEXT DEFAULT '[]'
);

-- 2. Create the papers table
CREATE TABLE papers (
    id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES research_sessions(id) ON DELETE CASCADE,
    title TEXT,
    authors TEXT,
    journal TEXT,
    year INTEGER,
    abstract TEXT,
    file_path TEXT,
    parsed_text TEXT
);
```

3. Navigate to **Project Settings → API** to locate your credentials:
   * **Project URL** (`SUPABASE_URL`)
   * **API Key / Anon Public** (`SUPABASE_KEY`)

---

## 2. Backend Deployment (FastAPI on Render)

We recommend **[Render](https://render.com/)** due to its easy Python setup and generous free tier.

### Step 2.1: Create a Render Web Service
1. Sign in to Render and click **New → Web Service**.
2. Connect your GitHub repository.
3. Configure the service settings:
   * **Name**: `scholarmind-backend`
   * **Language**: `Python 3`
   * **Root Directory**: `backend`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python -m app.api.main` (or `uvicorn app.api.main:app --host 0.0.0.0 --port $PORT` if calling custom WSGI)

### Step 2.2: Add Environment Variables
Under the **Environment** tab, add the following variables:
* `GEMINI_API_KEY`: *Your rotated Google Gemini key*
* `SUPABASE_URL`: *Your Supabase URL*
* `SUPABASE_KEY`: *Your Supabase API key*
* `PORT`: `8000`

Click **Deploy Web Service**. Once deployed, Render will provide a public URL (e.g. `https://scholarmind-backend.onrender.com`).

---

## 3. Frontend Deployment (Next.js on Vercel)

We recommend **[Vercel](https://vercel.com/)** (the creators of Next.js) for optimal hosting.

### Step 3.1: Configure Vercel Project
1. Sign in to Vercel and click **Add New → Project**.
2. Select your `ScholarMind` GitHub repository.
3. In the project settings, configure:
   * **Framework Preset**: `Next.js`
   * **Root Directory**: `frontend`

### Step 3.2: Environment Variables
Add the following key-value pair under **Environment Variables**:
* `NEXT_PUBLIC_API_URL`: *The URL of your deployed Render backend* (e.g., `https://scholarmind-backend.onrender.com`)

Click **Deploy**. Vercel will build your React components and compile static assets in seconds, yielding your live web application URL (e.g., `https://scholarmind.vercel.app`).
