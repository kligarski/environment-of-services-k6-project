# k6 - Testing with Grafana
This directory contains k6 load tests for the MCP server. Tests are executed in Kubernetes using the k6 Operator and a custom `k6-xk6-mcp` image that includes the `xk6-mcp` extension.

The tests simulate AI agents calling tools exposed by the MCP server and export metrics through OpenTelemetry to Prometheus and Grafana.


## Currently available tests

1. **connection-test**  
   Tests connection to all tools of the MCP server.

2. **validation-test**  
   Tests validation and error handling of the MCP server tools.

3. **list-products-load-test**  
   Tests the `list_products` tool under load.

4. **shipping-quote-load-test**  
   Tests the `get_shipping_quote` tool under load.

5. **packaging-load-test**  
   Tests the `optimize_packaging` tool under load.

6. **packaging-standard-load-test**  
   Tests the `optimize_packaging` tool under ligther traffic.

7. **mixed-load-test**  
   Tests all MCP server tools together under load.

## Running Tests

Each test consists of:

- a JavaScript test script in k6/tests/scripts/
- a Kubernetes TestRun manifest in k6/tests/manifests/
- a ConfigMap created from the JavaScript script before running the test


**Make sure Kubernetes stack is running, if not execute**:
```bash
./k8s/start_minikube.sh
```

### Running Single Test for test <test_name>:

#### Step 1: Clean up previous runs
If a test with the <test_name> already exists, delete the previous TestRun and ConfigMap first:

```bash
kubectl delete testrun mcp-<test_name> --ignore-not-found=true
kubectl delete configmap k6-<test_name>-script --ignore-not-found=true
```

#### Step 2: Create the ConfigMap

Create a ConfigMap for the test script and helper file (note: helper is not needed for connection-test):

```bash
kubectl create configmap k6-<test_name>-script \
  --from-file=<test_name>.js=k6/tests/scripts/<test_name>.js \
  --from-file=helpers.js=k6/tests/scripts/helpers.js
```

#### Step 3: Apply manifest and verify

```bash
kubectl apply -f k6/tests/manifests/<test_name>.yaml

kubectl get pods

kubectl logs -l k6_cr=<test_name>
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