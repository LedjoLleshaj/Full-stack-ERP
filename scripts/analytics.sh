#!/bin/bash
# =============================================================================
# ANALYTICS REPORT GENERATOR
# =============================================================================
# Generates an HTML analytics report from nginx access logs using GoAccess.
#
# Usage:
#   ./scripts/analytics.sh              # Analyze today's logs
#   ./scripts/analytics.sh --all        # Analyze ALL logs (including rotated)
#   ./scripts/analytics.sh --days 7     # Analyze last 7 days
#
# Prerequisites (one-time install on VPS):
#   sudo apt-get install -y goaccess
#
# The report is saved to: ~/reports/analytics_<date>.html
# Open it in your browser to explore the dashboard.
# =============================================================================

set -euo pipefail

# --- Configuration ---
APP_DIR="$HOME/apps/selita-fish"
LOG_DIR="$APP_DIR/logs/nginx"
REPORT_DIR="$HOME/reports"
DATE=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/analytics_$DATE.html"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helpers ---
info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Preflight checks ---
if ! command -v goaccess &> /dev/null; then
    error "GoAccess is not installed. Install it with: sudo apt-get install -y goaccess"
fi

if [ ! -d "$LOG_DIR" ]; then
    error "Nginx log directory not found at $LOG_DIR"
fi

# --- Parse arguments ---
MODE="current"  # current | all | days
DAYS=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all)
            MODE="all"
            shift
            ;;
        --days)
            MODE="days"
            DAYS="${2:-7}"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--all | --days N]"
            echo ""
            echo "  (no args)   Analyze the current access.log only"
            echo "  --all       Analyze all logs including rotated (access.log.*)"
            echo "  --days N    Analyze logs from the last N days (default: 7)"
            exit 0
            ;;
        *)
            warn "Unknown argument: $1"
            shift
            ;;
    esac
done

# --- Build the log file list ---
LOG_FILES=""

case "$MODE" in
    current)
        LOG_FILES="$LOG_DIR/access.log"
        if [ ! -f "$LOG_FILES" ]; then
            error "No access.log found at $LOG_FILES"
        fi
        info "Analyzing current access.log..."
        ;;
    all)
        # Combine current + rotated logs (gzip and plain)
        LOG_FILES=$(find "$LOG_DIR" -name "access.log*" -type f | sort)
        if [ -z "$LOG_FILES" ]; then
            error "No access log files found in $LOG_DIR"
        fi
        info "Analyzing ALL log files..."
        ;;
    days)
        LOG_FILES=$(find "$LOG_DIR" -name "access.log*" -type f -mtime "-$DAYS" | sort)
        if [ -z "$LOG_FILES" ]; then
            error "No log files found from the last $DAYS days in $LOG_DIR"
        fi
        info "Analyzing logs from the last $DAYS days..."
        ;;
esac

# --- Create report directory ---
mkdir -p "$REPORT_DIR"

# --- Generate report ---
# Handle potential gzipped rotated logs by decompressing on the fly
TEMP_LOG=$(mktemp)
trap "rm -f $TEMP_LOG" EXIT

for f in $LOG_FILES; do
    if [[ "$f" == *.gz ]]; then
        zcat "$f" >> "$TEMP_LOG"
    else
        cat "$f" >> "$TEMP_LOG"
    fi
done

LINE_COUNT=$(wc -l < "$TEMP_LOG" | tr -d ' ')
if [ "$LINE_COUNT" -eq 0 ]; then
    warn "Log files are empty — no traffic recorded yet."
    rm -f "$TEMP_LOG"
    exit 0
fi

info "Processing $LINE_COUNT log lines..."

goaccess "$TEMP_LOG" \
    --log-format=COMBINED \
    --output="$REPORT_FILE" \
    --html-report-title="Selita Fish Analytics" \
    --ignore-crawlers \
    --real-os \
    --agent-list \
    --no-query-string \
    2>/dev/null

info "Report generated: $REPORT_FILE"
info "Size: $(du -h "$REPORT_FILE" | cut -f1)"
echo ""
echo -e "${GREEN}To view the report:${NC}"
echo "  1. Download it:  scp your-vps:$REPORT_FILE ."
echo "  2. Open in browser: open analytics_$DATE.html"
echo ""

# --- Quick summary from GoAccess (text mode) ---
info "Quick summary:"
echo "-------------------------------------------"
goaccess "$TEMP_LOG" \
    --log-format=COMBINED \
    --no-query-string \
    --ignore-crawlers \
    --no-progress \
    --output=/dev/stdout \
    2>/dev/null | head -30 || true
echo "-------------------------------------------"
