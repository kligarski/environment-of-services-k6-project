#!/bin/bash
set -e

run_test() {
  TEST_NAME="$1"
  CONFIGMAP_NAME="$2"
  YAML_FILE="$3"
  WAIT_SECONDS="$4"

  echo "====================================="
  echo "Running $TEST_NAME"
  echo "====================================="

  kubectl delete testrun "$TEST_NAME" --ignore-not-found=true
  kubectl delete configmap "$CONFIGMAP_NAME" --ignore-not-found=true

  kubectl apply -f "$YAML_FILE"

  echo "Waiting ${WAIT_SECONDS}s..."
  sleep "$WAIT_SECONDS"

  kubectl get pods
  kubectl logs -l "k6_cr=$TEST_NAME" --tail=80 || true
}

run_test "mcp-connection-test" "k6-connection-test-script" "k6/tests/connection-test.yaml" 45
run_test "mcp-validation-test" "k6-validation-test-script" "k6/tests/validation-test.yaml" 30
run_test "mcp-stress-test-normal" "k6-stress-test-normal-script" "k6/tests/stress-test-normal.yaml" 80
run_test "mcp-stress-test-packaging" "k6-stress-test-packaging-script" "k6/tests/stress-test-packaging.yaml" 200
run_test "mcp-stress-test-all" "k6-stress-test-all-script" "k6/tests/stress-test-all.yaml" 150

echo "All tests finished/submitted."
kubectl get testrun
kubectl get pods