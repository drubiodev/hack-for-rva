# Procurement Frontend — Next.js 16 Dashboard

Built with [Next.js 16](https://nextjs.org), shadcn/ui, TanStack Query, and Recharts.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local` to point to the backend.

## Deploy on Azure Container Apps

The frontend deploys as a container to Azure Container Apps via Azure Container Registry:

```bash
# Build and push to ACR
az acr build --registry <acr-name> --image procurement-frontend:latest .

# Deploy to Container Apps
az containerapp create --name procurement-frontend \
  --resource-group <rg> --environment <env> \
  --image <acr-name>.azurecr.io/procurement-frontend:latest \
  --target-port 3000 --ingress external

# Set environment variables
az containerapp update --name procurement-frontend \
  --resource-group <rg> \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://<backend-app>.azurecontainerapps.io"
```

Ensure `output: "standalone"` is set in `next.config.ts` for optimized container builds.
