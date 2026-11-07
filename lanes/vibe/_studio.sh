# Shared by the vibe lane scripts: find (or build) Vibe Studio's binaries and the job's project file.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STUDIO="$REPO/studio"
pick_bin() {   # newest of release/debug; build the dev profile when neither exists
  local name="$1" b
  for b in "$STUDIO/target/release/$name" "$STUDIO/target/debug/$name"; do [[ -x "$b" ]] && { echo "$b"; return; }; done
  echo "building $name (first run takes ~10 min)…" >&2
  (cd "$STUDIO" && cargo build -q -p filmcraft -p filmcraft-cli) >&2 || return 1
  echo "$STUDIO/target/debug/$name"
}
job_slug() { grep -E '^job:' "$1/RUN.md" | awk '{print $2}' | head -1; }
job_project() { local s; s="$(job_slug "$1")"; echo "$1/vibe/${s:-$(basename "$1")}.vibeproj"; }
# make <job>/vibe/<slug>.vibeproj from the pipeline's files unless it exists (hand edits live in it)
ensure_project() {
  local job="$1" proj cli
  proj="$(job_project "$job")"
  [[ -f "$proj" && "${2:-}" != "--fresh" ]] && { echo "$proj"; return; }
  cli="$(pick_bin vibe-studio-cli)" || return 1
  mkdir -p "$(dirname "$proj")"
  local script; script="$(mktemp)"
  python3 - "$job" "$proj" > "$script" <<'PY'
import json, sys
job, proj = sys.argv[1], sys.argv[2]
for line in [{"id": "file.newProject", "params": {"name": proj.rsplit("/", 1)[-1].removesuffix(".vibeproj")}},
             {"id": "vibe.importJob", "params": {"dir": job}},
             {"id": "file.saveAs", "params": {"path": proj}}]:
    print(json.dumps(line))
PY
  "$cli" run "$script" >&2 || { rm -f "$script"; return 1; }
  rm -f "$script"
  echo "$proj"
}
