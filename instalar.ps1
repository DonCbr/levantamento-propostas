# Instala o necessario para o processo Levantamento -> Propostas (Windows 10/11).
# Uso: powershell -ExecutionPolicy Bypass -File .\instalar.ps1
$ErrorActionPreference = 'Stop'
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$pend = @()

function Tem($cmd) { $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }
function Winget($id) {
    Write-Host "  instalando $id ..."
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements | Out-Null
    if ($LASTEXITCODE -ne 0) { $script:pend += "Falhou instalar $id (rode: winget install --id $id)" }
}

Write-Host '1) Programas'
if (-not (Tem 'py'))  { Winget 'Python.Python.3.14' }   else { Write-Host '  ok  Python' }
if (-not (Tem 'node')) { Winget 'OpenJS.NodeJS.LTS' }   else { Write-Host '  ok  Node.js' }
if (-not (Tem 'git'))  { Winget 'Git.Git' }             else { Write-Host '  ok  Git' }
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')

Write-Host '2) Pacotes Python'
if (Tem 'py') {
    py -m pip install -q --upgrade pip
    py -m pip install -q -r (Join-Path $aqui 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { $pend += 'Falhou: py -m pip install -r requirements.txt' } else { Write-Host '  ok  pywin32, shapely, numpy, pillow, pymupdf' }
} else { $pend += 'Python nao encontrado: abra um novo terminal e rode de novo.' }

Write-Host '3) Otimizador de modelos 3D (gltf-transform)'
if (Tem 'npx') {
    npx -y '@gltf-transform/cli@4' --version | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host '  ok  @gltf-transform/cli@4 em cache' } else { $pend += 'Falhou: npx -y @gltf-transform/cli@4 --version' }
} else { $pend += 'Node/npx nao encontrado: abra um novo terminal e rode de novo.' }

Write-Host '4) Skill do Claude Code'
$destino = Join-Path $env:USERPROFILE '.claude\skills\levantamento-cad'
New-Item -ItemType Directory -Force $destino | Out-Null
Copy-Item -Recurse -Force (Join-Path $aqui 'skill\levantamento-cad\*') $destino
Write-Host "  ok  copiada para $destino"
if (Tem 'claude') {
    claude mcp get playwright 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host '  dica: para conferir paginas no navegador, rode:'; Write-Host '        claude mcp add --scope user playwright -- cmd /c npx -y @playwright/mcp@latest' }
} else { $pend += 'Claude Code nao encontrado: instale em https://claude.com/claude-code' }

Write-Host '5) GstarCAD'
if (Test-Path 'Registry::HKEY_CLASSES_ROOT\Gcad.Application') { Write-Host '  ok  Gcad.Application registrado (automacao COM disponivel)' }
else { $pend += 'GstarCAD nao registrado para COM: instale o GstarCAD 2022 LT e abra-o uma vez.' }

Write-Host ''
if ($pend.Count) { Write-Host 'Pendencias:' -ForegroundColor Yellow; $pend | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow } }
else { Write-Host 'Tudo pronto. Proximo passo: docs\PROCESSO.md' -ForegroundColor Green }
