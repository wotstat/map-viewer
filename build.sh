#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

VERSION=1.6.0
while getopts 'v:' option; do
  case "$option" in
    v) VERSION=$OPTARG ;;
    *) exit 1 ;;
  esac
done
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z]+)*$ ]] || {
  echo 'Expected version: X.Y.Z' >&2
  exit 1
}

PYTHON=${PYTHON:-python2}
"$PYTHON" -B -c 'import sys; assert sys.version_info[:2] == (2, 7), "Python 2.7 required"'

rm -rf .build
mkdir -p .build dist
trap 'rm -rf .build' EXIT
cp -R res .build/res

./as3/build.sh
VERSION="$VERSION" perl -pi -e 's/\{\{VERSION\}\}/$ENV{VERSION}/g' \
  .build/res/scripts/client/gui/mods/wotstat_map_viewer/__init__.py
VERSION="$VERSION" perl -pe 's/\{\{VERSION\}\}/$ENV{VERSION}/g' meta.xml > .build/meta.xml

(
  cd .build
  "$PYTHON" -B -m compileall -q -d res res
  package="wotstat.map-viewer_${VERSION}"
  zip -q -0 -X "$package.wotmod" meta.xml
  zip -q -r -0 -X "$package.wotmod" res -i '*.pyc' '*.swf' '*.png'
  cp "$package.wotmod" "../dist/$package.wotmod"
  cp "$package.wotmod" "../dist/$package.mtmod"
)
echo "Built dist/wotstat.map-viewer_${VERSION}.{wotmod,mtmod}"
