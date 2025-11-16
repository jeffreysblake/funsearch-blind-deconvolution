#!/bin/bash
# Test script for end-to-end convergence testing (no LM Studio required)

set -e

BASE_URL="http://localhost:7351"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🧪 FunSearch Convergence Test"
echo "=============================="
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if ! curl -s "${BASE_URL}/health" > /dev/null; then
    echo "❌ Backend is not running!"
    echo "   Please start it with: ./start-api.sh"
    exit 1
fi
echo "✅ Backend is running"
echo ""

# Choose example
echo "2. Choose example to run:"
echo "   [1] Number Sequence (5-10 min, 500 iterations)"
echo "   [2] Knapsack Heuristic (15-30 min, 1000 iterations)"
echo ""
read -p "Enter choice (1 or 2): " CHOICE

if [ "$CHOICE" == "1" ]; then
    SPEC_FILE="${SCRIPT_DIR}/examples/number_sequence/specification.py"
    PROJECT_NAME="Number Sequence Test"
    PROBLEM_TYPE="optimization"
    EVOLVE_FN="generate_number"
    EVAL_FN="evaluate"
    MAX_ITER=500
    NUM_ISLANDS=5
elif [ "$CHOICE" == "2" ]; then
    SPEC_FILE="${SCRIPT_DIR}/examples/knapsack/specification.py"
    PROJECT_NAME="Knapsack Heuristic Test"
    PROBLEM_TYPE="optimization"
    EVOLVE_FN="priority"
    EVAL_FN="evaluate"
    MAX_ITER=1000
    NUM_ISLANDS=10
else
    echo "❌ Invalid choice"
    exit 1
fi

# Verify spec file exists
if [ ! -f "$SPEC_FILE" ]; then
    echo "❌ Specification file not found: $SPEC_FILE"
    exit 1
fi

echo "✅ Using spec: $SPEC_FILE"
echo ""

# Create project
echo "3. Creating project..."
PROJECT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/projects" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"${PROJECT_NAME}\",
    \"description\": \"Automated convergence test\",
    \"problem_type\": \"${PROBLEM_TYPE}\",
    \"specification\": {
      \"file_path\": \"${SPEC_FILE}\",
      \"evolve_function\": \"${EVOLVE_FN}\",
      \"evaluate_function\": \"${EVAL_FN}\"
    }
  }")

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | jq -r '.id')

if [ "$PROJECT_ID" == "null" ] || [ -z "$PROJECT_ID" ]; then
    echo "❌ Failed to create project"
    echo "Response: $PROJECT_RESPONSE"
    exit 1
fi

echo "✅ Project created: $PROJECT_ID"
echo ""

# Create and start experiment
echo "4. Starting experiment..."
EXPERIMENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/projects/${PROJECT_ID}/experiments" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Convergence Test $(date +%Y%m%d_%H%M%S)\",
    \"config\": {
      \"llm\": {
        \"provider\": \"mock\",
        \"temperature\": 1.0
      },
      \"sandbox\": {
        \"provider\": \"subprocess\"
      },
      \"funsearch\": {
        \"samples_per_prompt\": 4,
        \"num_islands\": ${NUM_ISLANDS},
        \"reset_period\": 1800
      },
      \"execution\": {
        \"max_iterations\": ${MAX_ITER}
      }
    }
  }")

EXPERIMENT_ID=$(echo "$EXPERIMENT_RESPONSE" | jq -r '.id')

if [ "$EXPERIMENT_ID" == "null" ] || [ -z "$EXPERIMENT_ID" ]; then
    echo "❌ Failed to create experiment"
    echo "Response: $EXPERIMENT_RESPONSE"
    exit 1
fi

echo "✅ Experiment started: $EXPERIMENT_ID"
echo ""

# Show instructions for monitoring
echo "5. Monitoring options:"
echo ""
echo "   A. Watch via API (poll every 5 seconds):"
echo "      watch -n 5 \"curl -s ${BASE_URL}/api/v1/experiments/${EXPERIMENT_ID} | jq '{status, iterations_completed, best_score}'\""
echo ""
echo "   B. Watch via WebSocket:"
echo "      websocat ws://localhost:7351/ws/experiments/${EXPERIMENT_ID}"
echo "      # Then send: {\"type\": \"subscribe\", \"channels\": [\"metrics\", \"logs\", \"status\"]}"
echo ""
echo "   C. Check in browser:"
echo "      http://localhost:7350/projects/${PROJECT_ID}/experiments/${EXPERIMENT_ID}"
echo ""

# Simple polling monitor
read -p "Start simple monitor? (y/n): " MONITOR

if [ "$MONITOR" == "y" ]; then
    echo ""
    echo "📊 Monitoring experiment (Ctrl+C to stop)..."
    echo "Iteration | Status    | Best Score | Time"
    echo "----------------------------------------------"

    START_TIME=$(date +%s)

    while true; do
        sleep 5

        STATUS_RESPONSE=$(curl -s "${BASE_URL}/api/v1/experiments/${EXPERIMENT_ID}")

        STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')
        ITERATIONS=$(echo "$STATUS_RESPONSE" | jq -r '.iterations_completed')
        BEST_SCORE=$(echo "$STATUS_RESPONSE" | jq -r '.best_score // "N/A"')

        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        ELAPSED_MIN=$((ELAPSED / 60))
        ELAPSED_SEC=$((ELAPSED % 60))

        printf "%9s | %-9s | %10s | %02d:%02d\n" "$ITERATIONS" "$STATUS" "$BEST_SCORE" "$ELAPSED_MIN" "$ELAPSED_SEC"

        # Check if completed
        if [ "$STATUS" == "completed" ] || [ "$STATUS" == "failed" ] || [ "$STATUS" == "stopped" ]; then
            echo ""
            echo "🎉 Experiment finished with status: $STATUS"

            if [ "$STATUS" == "completed" ]; then
                echo ""
                echo "Final Results:"
                curl -s "${BASE_URL}/api/v1/experiments/${EXPERIMENT_ID}" | jq '{
                  iterations_completed,
                  best_score,
                  duration_seconds: ((.completed_at | fromdateiso8601) - (.started_at | fromdateiso8601))
                }'
            fi

            break
        fi
    done
fi

echo ""
echo "✅ Test complete!"
echo ""
echo "Project ID: $PROJECT_ID"
echo "Experiment ID: $EXPERIMENT_ID"
echo ""
