Param(
	[string]$Folder = "frontend/dist",
	[int]$Port = 8080
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Folder)) {
	throw "Dossier introuvable: $Folder (build web requis)."
}

Add-Type -AssemblyName System.Net.HttpListener
$prefix = "http://localhost:$Port/"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Host "Served: $Folder → $prefix (Ctrl+C pour arrêter)"

try {
	while ($true) {
		$ctx = $listener.GetContext()
		$request = $ctx.Request
		$response = $ctx.Response
		$rel = [Uri]::UnescapeDataString($request.Url.AbsolutePath.TrimStart('/'))
		if ([string]::IsNullOrWhiteSpace($rel)) { $rel = 'index.html' }
		$path = Join-Path (Resolve-Path $Folder) $rel
		if (-not (Test-Path $path)) {
			# SPA fallback
			$path = Join-Path (Resolve-Path $Folder) 'index.html'
		}
		$bytes = [System.IO.File]::ReadAllBytes($path)
		switch ([IO.Path]::GetExtension($path).ToLower()) {
			'.html' { $response.ContentType = 'text/html' }
			'.js'   { $response.ContentType = 'application/javascript' }
			'.css'  { $response.ContentType = 'text/css' }
			'.json' { $response.ContentType = 'application/json' }
			'.svg'  { $response.ContentType = 'image/svg+xml' }
			default { $response.ContentType = 'application/octet-stream' }
		}
		$response.OutputStream.Write($bytes, 0, $bytes.Length)
		$response.Close()
	}
} finally {
	$listener.Stop()
	$listener.Close()
}


