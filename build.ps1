param(
    [string]$Version = '1.6.0',
    [string]$Python = 'C:\Python27\python.exe',
    [string]$Royale = (Join-Path $env:LOCALAPPDATA 'Programs\ApacheRoyale\0.9.12\royale-asjs'),
    [string]$JavaHome = (Join-Path $env:LOCALAPPDATA 'Programs\MicrosoftOpenJDK\21')
)
$ErrorActionPreference = 'Stop'
if ($Version -notmatch '^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z]+)*$') { throw 'Invalid version' }
$projectRoot = $PSScriptRoot
$buildRoot = [IO.Path]::GetFullPath((Join-Path $projectRoot '.build'))
if ($buildRoot -ne (Join-Path $projectRoot '.build')) { throw 'Invalid staging path' }
if (Test-Path -LiteralPath $buildRoot) { Remove-Item -LiteralPath $buildRoot -Recurse -Force }
New-Item -ItemType Directory -Path "$buildRoot\res\gui\flash", "$projectRoot\dist" -Force | Out-Null
Copy-Item -LiteralPath "$projectRoot\res\scripts" -Destination "$buildRoot\res" -Recurse
Copy-Item -LiteralPath "$projectRoot\res\gui\maps" -Destination "$buildRoot\res\gui" -Recurse
$sdk = $Royale
$env:JAVA_HOME = $JavaHome
& "$sdk\bin\mxmlc.bat" '-compiler.targets=SWF' '-target-player=17.0' '-swf-version=17' '-debug=false' "-compiler.source-path=$projectRoot\as3\src" "-compiler.external-library-path=$projectRoot\as3\libs,$sdk\frameworks\libs\player\17.0\playerglobal.swc" "-output=$buildRoot\res\gui\flash\wotstatMapViewer.swf" "$projectRoot\as3\src\wotstat\mapviewer\MapBridge.as"
if ($LASTEXITCODE -ne 0) { throw 'AS3 compilation failed' }
& "$sdk\bin\mxmlc.bat" '-compiler.targets=SWF' '-target-player=17.0' '-swf-version=17' '-debug=false' "-compiler.source-path=$projectRoot\as3\src" "-compiler.external-library-path=$projectRoot\as3\libs,$sdk\frameworks\libs\player\17.0\playerglobal.swc" "-output=$buildRoot\res\gui\flash\wotstatMapViewerSelector.swf" "$projectRoot\as3\src\wotstat\mapviewer\MapSelector.as"
if ($LASTEXITCODE -ne 0) { throw 'Selector AS3 compilation failed' }
& "$sdk\bin\mxmlc.bat" '-compiler.targets=SWF' '-target-player=17.0' '-swf-version=17' '-debug=false' "-compiler.source-path=$projectRoot\as3\src" "-compiler.external-library-path=$projectRoot\as3\libs,$sdk\frameworks\libs\player\17.0\playerglobal.swc" "-output=$buildRoot\res\gui\flash\wotstatMapViewerBattle.swf" "$projectRoot\as3\src\wotstat\mapviewer\BattleBridge.as"
if ($LASTEXITCODE -ne 0) { throw 'Battle AS3 compilation failed' }
& $Python "$projectRoot\tools\package.py" $Version
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed' }
