param([string]$Version = '1.4.3', [string]$Python = 'C:\Python27\python.exe')
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$buildRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.build'))
if ($buildRoot -ne (Join-Path $projectRoot '.build')) { throw 'Invalid staging path' }
if (Test-Path -LiteralPath $buildRoot) { Remove-Item -LiteralPath $buildRoot -Recurse -Force }
New-Item -ItemType Directory -Path "$buildRoot\res\gui\flash", "$projectRoot\dist" -Force | Out-Null
Copy-Item -LiteralPath "$projectRoot\res\scripts" -Destination "$buildRoot\res" -Recurse
$sdk = Join-Path $env:LOCALAPPDATA 'Programs\ApacheRoyale\0.9.12\royale-asjs'
$env:JAVA_HOME = Join-Path $env:LOCALAPPDATA 'Programs\MicrosoftOpenJDK\21'
& "$sdk\bin\mxmlc.bat" '-compiler.targets=SWF' '-target-player=17.0' '-swf-version=17' '-debug=false' "-compiler.source-path=$projectRoot\as3\src" "-compiler.external-library-path=$projectRoot\as3\libs,$sdk\frameworks\libs\player\17.0\playerglobal.swc" "-output=$buildRoot\res\gui\flash\wotstatLocalMaps.swf" "$projectRoot\as3\src\wotstat\localmaps\MapBridge.as"
if ($LASTEXITCODE -ne 0) { throw 'AS3 compilation failed' }
& "$sdk\bin\mxmlc.bat" '-compiler.targets=SWF' '-target-player=17.0' '-swf-version=17' '-debug=false' "-compiler.source-path=$projectRoot\as3\src" "-compiler.external-library-path=$projectRoot\as3\libs,$sdk\frameworks\libs\player\17.0\playerglobal.swc" "-output=$buildRoot\res\gui\flash\wotstatLocalMapsSelector.swf" "$projectRoot\as3\src\wotstat\localmaps\MapSelector.as"
if ($LASTEXITCODE -ne 0) { throw 'Selector AS3 compilation failed' }
& "$sdk\bin\mxmlc.bat" '-compiler.targets=SWF' '-target-player=17.0' '-swf-version=17' '-debug=false' "-compiler.source-path=$projectRoot\as3\src" "-compiler.external-library-path=$projectRoot\as3\libs,$sdk\frameworks\libs\player\17.0\playerglobal.swc" "-output=$buildRoot\res\gui\flash\wotstatLocalMapsBattle.swf" "$projectRoot\as3\src\wotstat\localmaps\BattleBridge.as"
if ($LASTEXITCODE -ne 0) { throw 'Battle AS3 compilation failed' }
& $Python "$projectRoot\tools\package.py" $Version
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed' }
