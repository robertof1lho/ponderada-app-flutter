# AlterMe - Pipeline de inicializacao completa
param(
    [switch]$Down,
    [switch]$Rebuild,
    [switch]$Logs
)

$Root = $PSScriptRoot

function Write-Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "    [OK] $msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "    [ERRO] $msg" -ForegroundColor Red
    exit 1
}

# ── Parar tudo ─────────────────────────────────────────────────────────────────
if ($Down) {
    Write-Step "Parando todos os servicos..."
    docker compose -f "$Root\docker-compose.yml" down -v
    Write-Ok "Servicos parados e volumes removidos."
    exit 0
}

# ── Ver logs ───────────────────────────────────────────────────────────────────
if ($Logs) {
    docker compose -f "$Root\docker-compose.yml" logs -f
    exit 0
}

# ── Verificar pre-requisitos ───────────────────────────────────────────────────
Write-Step "Verificando pre-requisitos..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Fail "Docker nao encontrado. Instale Docker Desktop: https://www.docker.com/products/docker-desktop"
}
Write-Ok "Docker encontrado"

$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Docker Desktop nao esta rodando. Abra o Docker Desktop e tente novamente."
}
Write-Ok "Docker Desktop esta rodando"

# ── Subir servicos ─────────────────────────────────────────────────────────────
Write-Step "Subindo MySQL, MinIO e Backend..."

$composeArgs = @("-f", "$Root\docker-compose.yml", "up", "-d")
if ($Rebuild) { $composeArgs += "--build" }

docker compose @composeArgs
if ($LASTEXITCODE -ne 0) { Write-Fail "Falha ao subir containers" }
Write-Ok "Containers iniciados"

# ── Aguardar MySQL ─────────────────────────────────────────────────────────────
Write-Step "Aguardando MySQL ficar pronto..."
$tries = 0
do {
    Start-Sleep -Seconds 3
    $tries++
    $health = docker inspect --format="{{.State.Health.Status}}" alterme-mysql 2>&1
    Write-Host "    MySQL status: $health (tentativa $tries/20)"
} while ($health -ne "healthy" -and $tries -lt 20)

if ($health -ne "healthy") { Write-Fail "MySQL nao ficou pronto a tempo" }
Write-Ok "MySQL pronto"

# ── Aguardar MinIO ─────────────────────────────────────────────────────────────
Write-Step "Aguardando MinIO ficar pronto..."
$tries = 0
do {
    Start-Sleep -Seconds 3
    $tries++
    $health = docker inspect --format="{{.State.Health.Status}}" alterme-minio 2>&1
    Write-Host "    MinIO status: $health (tentativa $tries/20)"
} while ($health -ne "healthy" -and $tries -lt 20)

if ($health -ne "healthy") { Write-Fail "MinIO nao ficou pronto a tempo" }
Write-Ok "MinIO pronto"

# ── Aguardar Backend ───────────────────────────────────────────────────────────
Write-Step "Aguardando Backend ficar pronto..."
$tries = 0
do {
    Start-Sleep -Seconds 3
    $tries++
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        $backendReady = ($resp.StatusCode -eq 200)
    } catch {
        $backendReady = $false
    }
    Write-Host "    Backend pronto: $backendReady (tentativa $tries/20)"
} while (-not $backendReady -and $tries -lt 20)

if (-not $backendReady) { Write-Fail "Backend nao ficou pronto a tempo. Rode '.\start.ps1 -Logs' para ver erros." }
Write-Ok "Backend pronto"

# ── Resumo ─────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  AlterMe rodando com sucesso!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend API:      http://localhost:8000"       -ForegroundColor White
Write-Host "  Documentacao:     http://localhost:8000/docs"  -ForegroundColor White
Write-Host "  MinIO Console:    http://localhost:9001"       -ForegroundColor White
Write-Host "    Usuario: minioadmin  Senha: minioadmin"      -ForegroundColor Gray
Write-Host "  MySQL:            localhost:3306 (db: alterme)" -ForegroundColor White
Write-Host "    Usuario: root  Senha: password"              -ForegroundColor Gray
Write-Host ""
Write-Host "  Para parar tudo:  .\start.ps1 -Down"          -ForegroundColor Yellow
Write-Host "  Para ver logs:    .\start.ps1 -Logs"          -ForegroundColor Yellow
Write-Host "  Para rebuild:     .\start.ps1 -Rebuild"       -ForegroundColor Yellow
Write-Host ""
