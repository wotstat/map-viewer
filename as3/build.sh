#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p ../.build/res/gui/flash
for target in MapBridge:MapViewer MapSelector:MapViewerSelector BattleBridge:MapViewerBattle; do
  "${MXMLC:-mxmlc}" -load-config+=build-config.xml \
    -output="../.build/res/gui/flash/wotstat${target#*:}.swf" \
    "src/wotstat/mapviewer/${target%:*}.as"
done
