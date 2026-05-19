# k6 - Testing with Grafana
This directory contains k6 load tests for the MCP server. Tests are executed in Kubernetes using the k6 Operator and a custom `k6-xk6-mcp` image that includes the `xk6-mcp` extension.

The tests simulate AI agents calling tools exposed by the MCP server and export metrics through OpenTelemetry to Prometheus and Grafana.

## Currently available tests

1. **connection-test**: Tests connection to all tools of mcp server
2. **validation-test**: Tests validation of all tools of mcp server
3. **stress-test-normal**: Tests all tools of mcp server under normal level of stress
4. **stress-test-packaging**: Tests `optimize-packaging` tool under stress
5. **stress-test-all**: Tests all tools of mcp server under stress

## Running Tests

**Make sure Kubernetes stack is running, if not execute**:
```bash
./k8s/start_minikube.sh
```

### Running Single Test

**If a test with the <test_name> already exists, delete the previous TestRun and ConfigMap first:**

```bash
kubectl delete testrun mcp-<test_name>--ignore-not-found=true
kubectl delete configmap k6-<test_name>-script --ignore-not-found=true
```

**Running test for test <test_name>**:

```bash
kubectl apply -f k6/tests/<test_name>.yaml

kubectl get pods

kubectl logs -l k6_cr=<test_name>-test
```

### Running All Tests

```bash
./k6/run-all-tests.sh
```


### View Results
Watch progress with kubectl get pods — a Job pod will appear and run the test. Metrics will appear in Grafana under the **k6 Tests** dashboard in real time.
 
To access Grafana from your host:
```bash
kubectl port-forward service/grafana-service 3000:3000
```
Then open http://localhost:3000 (default credentials: admin / admin).