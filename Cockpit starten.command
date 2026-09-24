#!/bin/zsh
# Doppelklick im Finder: startet den lokalen Preview-Server und öffnet das Verbrauchs-Cockpit.
# Fenster schließen oder Ctrl+C beendet den Server.
cd "${0:A:h}" || exit 1

PORT="${PORT:-4173}"
URL="http://127.0.0.1:${PORT}/design-system/ui_kits/verbrauchs-cockpit/index.html"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js nicht gefunden (benötigt >= 22). Installation: brew install node"
  read -k1 "?Taste drücken zum Schließen …"
  exit 1
fi

if curl -fs -o /dev/null "$URL"; then
  echo "Server läuft bereits – öffne Cockpit."
  open "$URL"
  exit 0
fi

(
  for _ in {1..50}; do
    curl -fs -o /dev/null "$URL" && { open "$URL"; exit 0; }
    sleep 0.1
  done
  echo "Server hat nicht rechtzeitig geantwortet: $URL"
) &

echo "Verbrauchs-Cockpit: $URL"
echo "Zum Beenden dieses Fenster schließen oder Ctrl+C drücken."
PORT="$PORT" exec node scripts/preview.mjs
