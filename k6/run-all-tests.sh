#!/bin/bash
set -e

wait_for_testrun() {
  TEST_NAME="$1"
  TIMEOUT_SECONDS="$2"

  echo "Waiting for $TEST_NAME to finish..."

  START_TIME=$(date +%s)

  while true; do
    STAGE=$(kubectl get testrun "$TEST_NAME" -o jsonpath='{.status.stage}' 2>/dev/null || echo "")

    echo "Current stage: ${STAGE:-unknown}"

    if [ "$STAGE" = "Finished" ] || [ "$STAGE" = "finished" ]; then
      echo "$TEST_NAME finished."
      break
    fi

    if [ "$STAGE" = "Error" ] || [ "$STAGE" = "error" ]; then
      echo "$TEST_NAME failed."
      break
    fi

    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    if [ "$ELAPSED" -gt "$TIMEOUT_SECONDS" ]; then
      echo "Timeout waiting for $TEST_NAME."
      break
    fi

    sleep 5
  done
}

run_test() {
  TEST_NAME="$1"
  CONFIGMAP_NAME="$2"
  SCRIPT_FILE="$3"
  MANIFEST_FILE="$4"
  TIMEOUT_SECONDS="$5"

  echo "====================================="
  echo "Running $TEST_NAME"
  echo "====================================="

  kubectl delete testrun "$TEST_NAME" --ignore-not-found=true
  kubectl delete configmap "$CONFIGMAP_NAME" --ignore-not-found=true

  kubectl create configmap "$CONFIGMAP_NAME" \
    --from-file="$(basename "$SCRIPT_FILE")=$SCRIPT_FILE" \
    --from-file=helpers.js=k6/tests/scripts/helpers.js \
    --dry-run=client -o yaml | kubectl apply -f -

  kubectl apply -f "$MANIFEST_FILE"

  wait_for_testrun "$TEST_NAME" "$TIMEOUT_SECONDS"

  kubectl get pods
  kubectl logs -l "k6_cr=$TEST_NAME" --tail=100 || true
}

run_test "mcp-connection-test" "k6-connection-test-script" \
  "k6/tests/scripts/connection-test.js" \
  "k6/tests/manifests/connection-test.yaml" \
  180

run_test "mcp-validation-test" "k6-validation-test-script" \
  "k6/tests/scripts/validation-test.js" \
  "k6/tests/manifests/validation-test.yaml" \
  180

run_test "mcp-list-products-load-test" "k6-list-products-load-test-script" \
  "k6/tests/scripts/list-products-load-test.js" \
  "k6/tests/manifests/list-products-load-test.yaml" \
  300

run_test "mcp-shipping-quote-load-test" "k6-shipping-quote-load-test-script" \
  "k6/tests/scripts/shipping-quote-load-test.js" \
  "k6/tests/manifests/shipping-quote-load-test.yaml" \
  300

run_test "mcp-packaging-load-test" "k6-packaging-load-test-script" \
  "k6/tests/scripts/packaging-load-test.js" \
  "k6/tests/manifests/packaging-load-test.yaml" \
  420

run_test "mcp-mixed-load-test" "k6-mixed-load-test-script" \
  "k6/tests/scripts/mixed-load-test.js" \
  "k6/tests/manifests/mixed-load-test.yaml" \
  300

echo "All tests finished."
kubectl get testrun
kubectl get pods
