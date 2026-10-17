#!/usr/bin/env bash
# deploy/smoke-test.sh
#
# Smoke test for the M2 stack: OpenEMS Edge and its UI, simulation only.
# It checks that the stack came up and that the seeded simulated chain is running.
# It changes nothing. It does not judge the simulated values: the simulated battery
# drains to 0 % within hours (the chain has no PV), so values are not asserted.
# Edge logs a few ERROR lines in its first seconds on every healthy start (see
# docs/runbook.md), so the error check ignores the first 60 s after the container
# started and, on a young stack, waits until it is 75 s old before judging.
#
# Run it with permission to use Docker (normally sudo):
#   sudo bash deploy/smoke-test.sh [--wait SECONDS]
#
#   --wait SECONDS   how long to wait for the first Debug Log line after a start
#                    (default 90)
#
# Settings come from deploy/.env, the file Compose uses. Variables already set in
# the environment win over the file (as in Compose), so a second copy of the stack
# can be tested with COMPOSE_PROJECT_NAME and different ports (see docs/runbook.md).
#
# Exit codes: 0 no check failed (skipped checks are listed), 1 a check failed,
#             2 bad usage or missing configuration.

set -u -o pipefail

WAIT=90
while [ $# -gt 0 ]; do
  case "$1" in
    --wait)
      if [ $# -lt 2 ]; then echo "--wait needs a number of seconds" >&2; exit 2; fi
      WAIT="$2"; shift 2 ;;
    -h|--help) sed -n '2,/^$/p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$WAIT" in ''|*[!0-9]*) echo "--wait needs a whole number of seconds" >&2; exit 2 ;; esac

cd "$(dirname "$0")" || exit 2
if [ ! -f .env ]; then
  echo "deploy/.env not found. Copy .env.example to .env first." >&2
  exit 2
fi

# Read KEY=VALUE lines from .env. Variables already set in the environment win.
load_env() {
  local line key value
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|'#'*) continue ;; esac
    key="${line%%=*}"
    value="${line#*=}"
    case "$key" in ''|*[!A-Za-z0-9_]*) continue ;; esac
    if [ -z "${!key+x}" ]; then export "$key=$value"; fi
  done < .env
}
load_env

for var in BIND_ADDRESS EDGE_FELIX_PORT UI_HTTP_PORT; do
  if [ -z "${!var:-}" ]; then
    echo "$var is not set in deploy/.env" >&2
    exit 2
  fi
done

# What the seeded chain should activate (see deploy/edge-seed/README.md). These are
# facts about the seed, not settings.
EXPECTED_ACTIVATIONS=(
  "Controller.Debug.Log"
  "Scheduler.AllAlphabetically"
  "Simulator.Datasource.CSV.Predefined"
  "Simulator.GridMeter.Acting"
  "Simulator.EssSymmetric.Reacting"
  "Controller.Symmetric.Balancing"
  "Controller.Api.Websocket"
  "Core.Energy"
)
LIVE_RE='ctrlDebugLog0\].*_sum\[.*ess0\[.*meter0\['
ROTATION_GRACE_S=120   # first log line later than this after container start = startup lines are missing
STEADY_IGNORE_S=60     # seconds after container start whose ERROR lines are ignored
STEADY_MIN_AGE_S=75    # a young stack is waited for until it is this old

PASS=0; FAIL=0; SKIP=0
report() { # status name detail
  printf '%-5s %-26s %s\n' "$1" "$2" "$3"
  case "$1" in PASS) PASS=$((PASS + 1)) ;; FAIL) FAIL=$((FAIL + 1)) ;; SKIP) SKIP=$((SKIP + 1)) ;; esac
}
info() { printf '%-5s %-26s %s\n' "INFO" "$1" "$2"; }

dc() { docker compose "$@"; }
http_code() {
  local code
  code=$(curl -sS --max-time 10 -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || true)
  [ -n "$code" ] || code=000
  printf '%s' "$code"
}
live_lines() { dc logs --no-log-prefix --since 20s openems-edge 2>&1 | grep -E "$LIVE_RE"; }
# Called when a log read returned nothing: tells a damaged log file (--tail still
# works) from Edge not logging at all. Docker prints no error for a damaged file.
log_hint() {
  if [ -n "$(dc logs --no-log-prefix --tail 1 openems-edge 2>&1 | head -n 1)" ]; then
    echo "but --tail still works, so the container log file may be damaged (see docs/runbook.md)"
  else
    echo "and --tail returns nothing either, so Edge may not be logging"
  fi
}

tmp=$(mktemp) || exit 2
trap 'rm -f "$tmp"' EXIT

echo "Smoke test: project '$(dc config 2>/dev/null | sed -n 's/^name: //p' | head -n 1)', waiting up to ${WAIT}s for the Debug Log"
waited=0
while [ "$waited" -lt "$WAIT" ] && [ -z "$(live_lines | tail -n 1)" ]; do
  sleep 3
  waited=$((waited + 3))
done

# 1. Containers: running, not out-of-memory-killed, never restarted; seed exited 0.
edge_id=""
for svc in openems-edge openems-ui; do
  id=$(dc ps -q "$svc" 2>/dev/null | head -n 1)
  [ "$svc" = "openems-edge" ] && edge_id="$id"
  if [ -z "$id" ]; then
    report FAIL "container $svc" "not found"
    continue
  fi
  state=$(docker inspect -f '{{.State.Running}} oom={{.State.OOMKilled}} restarts={{.RestartCount}}' "$id" 2>&1)
  if [ "$state" = "true oom=false restarts=0" ]; then
    report PASS "container $svc" "$state"
  else
    report FAIL "container $svc" "$state"
  fi
done
seed_id=$(dc ps -a -q openems-edge-seed 2>/dev/null | head -n 1)
if [ -z "$seed_id" ]; then
  report FAIL "container seed" "not found"
else
  code=$(docker inspect -f '{{.State.ExitCode}}' "$seed_id" 2>&1)
  if [ "$code" = "0" ]; then report PASS "seed exit code" "0"; else report FAIL "seed exit code" "$code"; fi
fi

# 2. The Felix console must ask for a login (401), never answer openly.
code=$(http_code "http://${BIND_ADDRESS}:${EDGE_FELIX_PORT}/system/console")
if [ "$code" = "401" ]; then report PASS "console is protected" "HTTP $code"; else report FAIL "console is protected" "HTTP $code (expected 401)"; fi

# 3. The UI answers.
code=$(http_code "http://${BIND_ADDRESS}:${UI_HTTP_PORT}/")
if [ "$code" = "200" ]; then report PASS "UI answers" "HTTP $code"; else report FAIL "UI answers" "HTTP $code (expected 200)"; fi

# Container start time, used by checks 4 and 6.
started=""
started_s=0
if [ -n "$edge_id" ]; then
  started=$(docker inspect -f '{{.State.StartedAt}}' "$edge_id" 2>&1)
  started_s=$(date -u -d "$started" +%s 2>/dev/null || echo 0)
fi

# 4. Startup: every expected component logged "Activate <factory PID>".
if [ -z "$edge_id" ]; then
  report FAIL "startup activations" "Edge container not found"
else
  dc logs --no-log-prefix --since "$started" openems-edge > "$tmp" 2>&1
  first=$(grep -m 1 -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}' "$tmp" || true)
  if [ ! -s "$tmp" ]; then
    report FAIL "startup activations" "Docker returned no log lines since the container started, $(log_hint)"
  elif [ -z "$first" ]; then
    report FAIL "startup activations" "log lines exist but none has a timestamp"
  else
    first_s=$(date -u -d "$first" +%s 2>/dev/null || echo 0)
    missing=()
    for pid in "${EXPECTED_ACTIVATIONS[@]}"; do
      grep -qF "Activate $pid" "$tmp" || missing+=("$pid")
    done
    if [ "${#missing[@]}" -eq 0 ]; then
      report PASS "startup activations" "all ${#EXPECTED_ACTIVATIONS[@]} found"
    elif [ $((first_s - started_s)) -gt "$ROTATION_GRACE_S" ]; then
      report SKIP "startup activations" "the first log line is more than ${ROTATION_GRACE_S}s after the container started (log rotated, or its start unreadable); recreate the stack to re-run this check"
    else
      report FAIL "startup activations" "missing: ${missing[*]}"
    fi
  fi
fi

# 5. Live: the Debug Log prints its summary line, naming the meter and battery.
lines=$(live_lines)
count=$(printf '%s\n' "$lines" | grep -c . || true)
if [ "$count" -ge 1 ]; then
  report PASS "Debug Log is live" "$count lines in the last 20 s"
  sum_state=$(printf '%s\n' "$lines" | tail -n 1 | grep -oE '_sum\[State:[A-Za-z]+' | head -n 1 | sed 's/^_sum\[State://')
  info "sum state" "${sum_state:-unknown} (informational, not a pass/fail criterion)"
  defekt=$(dc logs --no-log-prefix --since 60s openems-edge 2>&1 | grep -c 'Defekte App' || true)
  info "'Defekte App' lines" "$defekt in the last 60 s (informational; see docs/runbook.md)"
else
  raw=$(dc logs --no-log-prefix --since 20s openems-edge 2>&1 | grep -c . || true)
  if [ "$raw" -ge 1 ]; then
    report FAIL "Debug Log is live" "log lines exist but none is a Debug Log summary (is ctrlDebugLog0 configured?)"
  else
    report FAIL "Debug Log is live" "no log lines in the last 20 s, $(log_hint)"
  fi
fi

# 6. Steady state: no ERROR lines in the last minute, ignoring the first
#    STEADY_IGNORE_S seconds after the container started (known startup noise).
if [ -z "$edge_id" ]; then
  report FAIL "no recent errors" "Edge container not found"
else
  age=$(( $(date -u +%s) - started_s ))
  if [ "$age" -lt "$STEADY_MIN_AGE_S" ]; then
    echo "      (stack is ${age}s old; waiting $((STEADY_MIN_AGE_S - age))s so startup errors are out of the window)"
    sleep $((STEADY_MIN_AGE_S - age))
  fi
  now_s=$(date -u +%s)
  win_s=$((now_s - 60))
  floor_s=$((started_s + STEADY_IGNORE_S))
  if [ "$win_s" -lt "$floor_s" ]; then win_s=$floor_s; fi
  since=$(date -u -d "@$win_s" +%Y-%m-%dT%H:%M:%SZ)
  win_out=$(dc logs --no-log-prefix --since "$since" openems-edge 2>&1)
  win_lines=$(printf '%s\n' "$win_out" | grep -c . || true)
  errs=$(printf '%s\n' "$win_out" | grep -c ' ERROR ' || true)
  if [ "$win_lines" -eq 0 ]; then
    report FAIL "no recent errors" "no log lines at all in the last $((now_s - win_s)) s, so errors cannot be judged, $(log_hint)"
  elif [ "$errs" -eq 0 ]; then
    report PASS "no recent errors" "0 ERROR lines in the last $((now_s - win_s)) s"
  else
    report FAIL "no recent errors" "$errs ERROR lines in the last $((now_s - win_s)) s"
  fi
fi

echo "Result: $PASS passed, $FAIL failed, $SKIP skipped"
[ "$FAIL" -eq 0 ]
