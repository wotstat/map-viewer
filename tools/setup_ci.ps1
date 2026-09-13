param([Parameter(Mandatory = $true)][string]$Destination)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
$archive = Join-Path $Destination 'royale.zip'
Invoke-WebRequest -UseBasicParsing -Uri 'https://archive.apache.org/dist/royale/0.9.12/binaries/apache-royale-0.9.12-bin-js-swf.zip' -OutFile $archive
$expected = '7ece00f3de5ab6306a22763eab735e55d8c4b96cfbf653f8580b97bad501cfc66001590e16eb04699976d6e2b627a8bbfd993ed338374621315de2b9651c3628'
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA512).Hash -ne $expected) { throw 'Royale checksum mismatch' }
Expand-Archive -LiteralPath $archive -DestinationPath $Destination -Force
$compilers = @(Get-ChildItem -LiteralPath $Destination -Recurse -Filter mxmlc.bat | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.Directory.Parent.FullName 'frameworks/royale-config.xml')
})
if ($compilers.Count -ne 1) { throw 'Cannot locate Royale SDK' }
$sdk = $compilers[0].Directory.Parent.FullName
$playerDir = Join-Path $sdk 'frameworks/libs/player/17.0'
New-Item -ItemType Directory -Path $playerDir -Force | Out-Null
$player = Join-Path $playerDir 'playerglobal.swc'
Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/nexussays/playerglobal/fef560243029214656d83fc673be0267a1ea0816/17.0/playerglobal.swc' -OutFile $player
if ((Get-FileHash -LiteralPath $player -Algorithm SHA256).Hash -ne '58ecda7ac7de1a3add77cd880089c9edb0597bc8ac1c4bb0f9b4f5e13531b7a6') { throw 'playerglobal checksum mismatch' }
Write-Output $sdk
