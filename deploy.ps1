#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build and deploy the hack-for-rva procurement app to Azure Web App.

.DESCRIPTION
    1. Copies ui/ into the backend build context
    2. Builds a Docker image with the UI bundled
    3. Pushes to Azure Container Registry (hackforrvacr.azurecr.io)
    4. Restarts the Azure Web App to pull the new image

.PARAMETER Tag
    Docker image tag (default: git short SHA or "latest")

.EXAMPLE
    .\deploy.ps1
    .\deploy.ps1 -Tag v1.2
#>

param(
    [string]$Tag = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Config ────────────────────────────────────────────────────────────────────
$ACR           = "hackforrvacr.azurecr.io"
$ImageName     = "procurement-api"
$WebAppName    = "hackforrva"
$ResourceGroup = "hackathon-rva"
$SubscriptionId = "05bd7e85-2824-47d6-8f49-f52584dbf262"
$RepoRoot      = $PSScriptRoot

# ── Tag ───────────────────────────────────────────────────────────────────────
if (-not $Tag) {
    $gitSha = git -C $RepoRoot rev-parse --short HEAD 2>$null
    $Tag = if ($gitSha) { $gitSha } else { "latest" }
}

$FullImage = "$ACR/${ImageName}:${Tag}"
$LatestImage = "$ACR/${ImageName}:latest"

Write-Host "`n==> Deploying tag: $Tag" -ForegroundColor Cyan
Write-Host "    Image: $FullImage"

# ── Set subscription ──────────────────────────────────────────────────────────
Write-Host "`n==> Setting Azure subscription..." -ForegroundColor Cyan
az account set --subscription $SubscriptionId

# ── Copy ui/ into backend build context ──────────────────────────────────────
$UiSrc  = Join-Path $RepoRoot "ui"
$UiDest = Join-Path $RepoRoot "procurement\backend\ui"

Write-Host "`n==> Copying ui/ into backend build context..." -ForegroundColor Cyan
if (Test-Path $UiDest) { Remove-Item $UiDest -Recurse -Force }
Copy-Item $UiSrc $UiDest -Recurse

# ── ACR login ─────────────────────────────────────────────────────────────────
Write-Host "`n==> Logging into ACR..." -ForegroundColor Cyan
az acr login --name hackforrvacr

# ── Docker build ─────────────────────────────────────────────────────────────
Write-Host "`n==> Building Docker image..." -ForegroundColor Cyan
$BackendDir = Join-Path $RepoRoot "procurement\backend"
docker build `
    --platform linux/amd64 `
    -t $FullImage `
    -t $LatestImage `
    $BackendDir

if ($LASTEXITCODE -ne 0) { Write-Error "Docker build failed."; exit 1 }

# ── Docker push ──────────────────────────────────────────────────────────────
Write-Host "`n==> Pushing image to ACR..." -ForegroundColor Cyan
docker push $FullImage
docker push $LatestImage

if ($LASTEXITCODE -ne 0) { Write-Error "Docker push failed."; exit 1 }

# ── Update Web App container image ───────────────────────────────────────────
Write-Host "`n==> Updating Web App container image..." -ForegroundColor Cyan
az webapp config container set `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --container-image-name $LatestImage

# ── Restart Web App ───────────────────────────────────────────────────────────
Write-Host "`n==> Restarting Web App to pull new image..." -ForegroundColor Cyan
az webapp restart --name $WebAppName --resource-group $ResourceGroup

# ── Clean up copied ui/ from backend dir ─────────────────────────────────────
Write-Host "`n==> Cleaning up build context..." -ForegroundColor Cyan
if (Test-Path $UiDest) { Remove-Item $UiDest -Recurse -Force }

# ── Done ─────────────────────────────────────────────────────────────────────
$url = "https://${WebAppName}.azurewebsites.net"
Write-Host "`n==> Deployment complete!" -ForegroundColor Green
Write-Host "    URL: $url" -ForegroundColor Green
Write-Host "    Tag: $Tag`n"
