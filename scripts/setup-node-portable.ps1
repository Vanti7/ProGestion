Param(
	[string]$Version = "v20.17.0",
	[switch]$RunDev,
	[string]$Proxy = $env:HTTPS_PROXY
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Join-Path $env:USERPROFILE 'apps\node'
New-Item -ItemType Directory -Force -Path $root | Out-Null

$zipUrl = "https://nodejs.org/dist/$Version/node-$Version-win-x64.zip"
$zip    = Join-Path $root 'node.zip'

Write-Host "Téléchargement Node $Version depuis $zipUrl ..."
$ireq = @{ Uri = $zipUrl; OutFile = $zip }
if ($Proxy) { $ireq.Proxy = $Proxy }
Invoke-WebRequest @ireq

Write-Host 'Décompression...'
Expand-Archive -Path $zip -DestinationPath $root -Force
Remove-Item $zip -Force

$nodeDir = Join-Path $root "node-$Version-win-x64"
if (-not (Test-Path $nodeDir)) {
	# Fallback: détecter dynamiquement si le dossier exact n'existe pas
	$nodeDir = (Get-ChildItem $root -Directory | Where-Object Name -match '^node-v.*-win-x64$' | Select-Object -First 1).FullName
}
if (-not $nodeDir) { throw 'Dossier Node introuvable après extraction.' }

$nodeExe = Join-Path $nodeDir 'node.exe'
$npmCmd  = Join-Path $nodeDir 'npm.cmd'

& $nodeExe -v | Write-Host
& $npmCmd -v  | Write-Host

if ($RunDev) {
	Write-Host 'Installation des dépendances frontend...'
	Push-Location (Join-Path $PSScriptRoot '..\frontend')
	try {
		# Config proxy npm si HTTPS_PROXY défini
		if ($Proxy) {
			& $npmCmd "config" "set" "proxy" $Proxy | Out-Host
			& $npmCmd "config" "set" "https-proxy" $Proxy | Out-Host
		}
		& $npmCmd "install"
		Write-Host 'Lancement du serveur Vite (web)...'
		& $npmCmd "run" "dev"
	} finally {
		Pop-Location
	}
} else {
	Write-Host "Node installé en mode portable dans: $nodeDir"
	Write-Host 'Pour lier Node dans cette session:'
	Write-Host ("`$env:Path = '{0};' + `$env:Path" -f $nodeDir)
	Write-Host 'Pour démarrer le frontend:'
	Write-Host 'cd frontend; npm install; npm run dev'
}


