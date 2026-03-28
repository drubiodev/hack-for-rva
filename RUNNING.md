# Running the Project

## Step 1 — Start database

```powershell
docker start procurement-pg
```

## Step 2 — Start backend

> ⚠️ Must be in the `backend` folder, NOT `procurement`

```powershell
cd c:\repos\hack-for-rva\procurement\backend
$env:PYTHONPATH = $PWD
.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

- API: http://localhost:8000/api/v1
- Swagger docs: http://localhost:8000/docs
- UI (index): http://localhost:8000/
- UI (login): http://localhost:8000/login.html
- UI (document): http://localhost:8000/document.html

> The UI static files are served directly by FastAPI from `ui/`.
> No separate frontend server needed for the static UI.

## Step 3 — Deploy to Azure

```powershell
cd c:\repos\hack-for-rva
.\deploy.ps1
```

Builds and pushes to `hackforrvacr.azurecr.io`, updates `hackforrva.azurewebsites.net`.

## Step 4 — Next.js frontend (optional — only needed for the React dashboard)

```powershell
cd c:\repos\hack-for-rva\procurement\frontend
npm run dev
```

App: http://localhost:3000

## Step 5 — pgAdmin (optional, browser UI for PostgreSQL)

```powershell
docker run -d --name pgadmin -e PGADMIN_DEFAULT_EMAIL=admin@admin.com -e PGADMIN_DEFAULT_PASSWORD=admin -p 5050:80 dpage/pgadmin4
```

Open **http://localhost:5050** and login with `admin@admin.com` / `admin`.

To connect to the database, register a new server with:

- **Host:** `host.docker.internal`
- **Port:** `5432`
- **Database:** `procurement`
- **Username:** `postgres`
- **Password:** `postgres`

> If the container already exists: `docker start pgadmin`
