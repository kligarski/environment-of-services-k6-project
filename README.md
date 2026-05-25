# K6 - Using K6 project for application testing
This project is part of the 'Environment of Services' course at AGH University of Krakow (summer semester, 2026).

Authors:
- Jakub Ciura ([@jciura](https://github.com/jciura)),
- Bernard Gawor ([@Gawor270](https://github.com/Gawor270)),
- Krzysztof Ligarski ([@kligarski](https://github.com/kligarski)),
- Łukasz Zegar ([@lvk4z](https://github.com/lvk4z)).

## 1. Introduction
Large language models are currently on the rise, and with that many developers seek ways to use them in everyday applications. One concept that seems the most popular right now is the 
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro). It provides a standardized interface for connecting language models with external tools and services. LLMs, which are called in this instance AI agents, are used as middlemen between the user and the backend service. The agent interprets user's query and chooses proper tool that is available through MCP server.

As MCP servers become more widespread, it becomes increasingly important to evaluate their performance, limitations, and advantages. The main goal of this project is to design a demonstration environment that showcases xk6-mcp, a tool used for testing MCP servers. The environment will enable simulation of interactions with MCP servers and allow their behavior under load to be analyzed. Testing will be performed by collecting and visualizing metrics using [OpenTelemetry](https://opentelemetry.io/), [Prometheus](https://prometheus.io/) and [Grafana](https://grafana.com/). 

## 2. Theoretical background and technology stack
### 2.1 Application Layer
#### Chainlit
A Python framework for building interactive web applications.  
Used as the frontend interface in this project.

**Advantages:**
- Minimal amount of code required  
- Supports streaming tokens from LLMs (progressive responses)  

#### FastAPI
A modern, high-performance web framework for Python based on the ASGI standard. In the project, it serves two roles: the backend of the business application (REST API) and the transport layer for the MCP server (via FastMCP + SSE).

**Advantages:**
- Automatic OpenAPI documentation  
- Asynchronous execution  
- Native OpenTelemetry integration  

#### SQLite
A lightweight, serverless relational database. Persistence layer for the backend, stores domain data (e.g., products in inventory).

**Advantages:**
- Zero configuration, single file, suitable for demo
- Easy migration to other databases  

### 2.2 AI and Orchestration
#### LangChain
A framework for building applications based on LLM. Acts as the agent orchestrator and MCP client. Connects the language model with tools exposed by the MCP server.

**Features:**
- ReAct-style agents: LLM iteratively decides which tool to call based on tool descriptions from the MCP server
- Package langchain-mcp-adapters automatically converts MCP schemas into LangChain tool objects 
- Easy LLM switching (Gemini, Ollama, OpenAI)  

#### LLM Backends
**Google Gemini API** - cloud-based language models from Google.
- Native function/tool calling  
- Large context window  
- Access via `google-generativeai` SDK  

**Ollama** - running local LLM models. Optional backend for offline or private environments.
- No API costs, full privacy  
- Models: Llama 3, Mistral, Phi-3  
- OpenAI-compatible API  

#### FastMCP
Python library for building MCP servers.

**Features:**
- Define tools using `@mcp.tool()` decorator  
- Integrated with FastAPI  
- Implements MCP protocol for tool discovery and execution  

### 2.3 Testing
#### Grafana k6
An open-source tool for load and performance testing written in Go, with test scripts in JavaScript. Designed for embedding in CI/CD pipelines, natively integrates with the Grafana observability stack.

**Features:**
- Virtual users (VU) - concurrent goroutines, each independently executes a test script, easy simulation of dozens of parallel AI agents
- Built-in metrics:
  - http_req_duration
  - http_req_failed
  - iteration_duration
- Integration with OpenTelemetry and Prometheus  

#### xk6-mcp
A k6 extension adding native MCP client capabilities to test scripts. Allows communication with the MCP server using the full protocol instead of raw HTTP calls.

- Without xk6-mcp, JSON-RPC messages would have to be manually constructed over HTTP/SSE
- Allows validation not only of latency, but also correctness at the protocol level: whether tool schemas are valid, whether error codes are returned correctly

🔗 https://github.com/grafana/xk6-mcp  

### 2.4 Observability Stack
#### OpenTelemetry
A technology-neutral CNCF framework for generating, collecting, and exporting telemetry data. Central hub collecting metrics from all components.

#### Prometheus
An open-source toolkit for monitoring and alerting. Stores time series metrics and provides PromQL for querying.
Ingestion mode used in this project: Remote Write (OTel Collector pushes data to Prometheus).

#### Grafana
An open-source analytics and visualization platform. Connects to Prometheus and renders configurable dashboards.
Dashboards are auto-provisioned via ConfigMaps: **Services Overview** (backend and MCP server request rate and P95 latency) and **k6 Load Test** (VUs, MCP request rate, MCP duration, iteration duration).

### 2.5 Infrastructure – Kubernetes
A platform for container orchestration. The entire demo stack - application, MCP server, k6 operator, OTel collector, Prometheus and Grafana - is run on a Kubernetes cluster.

k6 Operator allows defining a load test as a Kubernetes manifest, tests can be triggered by CI pipeline via 'kubectl apply'

## 3. Demo concept description
### 3.1. Application
The application used to interact with an AI model is a simple chatbot. Its interface is implemented using Chainlit, which is an open-source Python framework that allows to deliver interactive data apps in only a few lines of code.

The chatbot uses LangChain to intergrate LLM with external tools that are available through MCP server. The LLM is responsible for interpreting user's request and choosing proper tool defined in mentioned previously MCP server.

The MCP server is implemented using FastMCP and exposes a set of tools that are related to operations implemented in backend service. These operations allow user to perform actions such as retrieving product information, listing available items and calculating shipping costs.

To evaluate the behavior of the MCP server under load, testing will be performed using k6 together with xk6-mcp. The testing environment will simulate multiple AI agents sending requests to the MCP server simultaneously. This allows the system to mimic realistic interaction patterns and analyze how the MCP server performs when handling concurrent requests generated by multiple agents.

### 3.2. Observability
In order to analyze the behavior and performance of the system, the demo is equipped with an observability layer based on OpenTelemetry, which collects metrics from all components.

To get the whole picture of the system state, k6, the backend service, and the MCP server export metrics to an OpenTelemetry Collector instance via OTLP/gRPC. The collector batches and forwards the data to Prometheus via Remote Write.

This setup enables the collection of various performance indicators from whole system, and that allows to truly measure how MCP server behaves under different workloads, identify potential bottlenecks and assess general state of system.

### 3.3. Visualization
To make analysis of the collected telemetry data easier, the system uses Grafana for visualization. Grafana connects to Prometheus and provides interactive dashboard along with real-time metrics generated by the system.

The dashboards present key performance indicators such as request throughput, response times, error rates, and resource utilization. By analyzing these metrics, it is possible to evaluate how MCP server and backend respond to changes. 

## 4. Demo high level architecture
![High level architecture](docs/img/high-level-architecture.png)

## 5. Demo detailed architecture
The architecture is designed using a microservices approach and adapted for deployment in orchestrated (Kubernetes/Minikube) environments.

*   **Backend Service (FastAPI):** A demo logistics system providing business logic for inventory and logistics management. It is intentionally designed with artificial delays and CPU loads to simulate real-world processing for performance testing.
    *   **Orchestration:** Deployed with **2 replicas** for high availability and load distribution. Includes **Liveness and Readiness probes** pointing to `/health`.
    *   `GET /products`: Provides product discovery with name filtering. Returns details like price, weight, and dimensions.
    *   `POST /shipping/quote`: Calculates shipping estimates. It simulates concurrent interactions with four different shipping providers' APIs, each with randomized network-like latency.
    *   `POST /packaging/optimize`: Implements a heuristic packaging algorithm. It calculates how to fit multiple items into standard box sizes and includes an artificial CPU-intensive load to simulate heavy computational tasks.
    *   **Data Persistence:** Uses a local **SQLite** database for storing product information.
*   **MCP Server (FastMCP):** Implements the Model Context Protocol and acts as a gateway for LLM Agents.
    *   **Orchestration:** Deployed with **2 replicas** to handle concurrent agent requests. Monitored via **TCP health checks** on port 8080.
    *   **Transport:** Uses **Streamable HTTP**, allowing for both standard request-response and SSE-based notifications/streaming.
    *   **Tooling:** Exposes three main tools: `list_products`, `get_shipping_quote`, and `optimize_packaging`, which directly map to the backend's REST endpoints.

*   **OTel Collector:** Receives metrics from all components via OTLP/gRPC (port 4317) and forwards them to Prometheus using Remote Write. Deployed as a single instance.
*   **Prometheus:** Configured with `--web.enable-remote-write-receiver` to accept pushed metrics. No scrape targets — all data comes from the OTel Collector.
*   **Grafana:** Dashboards are auto-provisioned at startup via ConfigMaps. Two dashboards are available:
    *   **Services Overview** — backend and MCP server HTTP metrics (request rate, P95 latency).
    *   **k6 Load Test** — k6 test metrics (virtual users, MCP request rate and duration, iteration duration).

*   **Frontend (Chainlit):** A web-based chatbot interface that provides a user-friendly way to interact with the AI Agent. Deployed as a single replica with **TCP health checks**.
*   **Agent (LangChain):** The orchestrator component (integrated with the Frontend) that uses the ReAct pattern to interpret user queries, select appropriate tools from the MCP server, and generate responses.
*   **Ollama / Gemini:** The environment supports switching between local and cloud-based LLM execution to demonstrate flexibility and performance trade-offs:
    *   **Gemini:** A cloud-based LLM (via API) providing high reasoning performance and native tool calling. It is generally faster for complex tasks but requires external connectivity.
    *   **Ollama:** A local LLM provider deployed within the cluster as a **single replica** with persistent storage for models. While it allows for completely offline and private interactions, local execution is typically slower than cloud APIs, and lighter models (like Llama 3.2 1B/3B) may exhibit lower "intelligence" or accuracy in complex tool selection compared to larger cloud models.

## 6. Environment configuration description
The primary demonstration environment is built around Kubernetes to allow for load testing and production environment simulation. 

Requirements for the local machine:
* An operating system with containerization support (Linux, macOS, or Windows with WSL2).
* Python 3.12+ environment (for running simple test scripts to verify the connection).
* Docker.
* Minikube and the `kubectl` tool configured to use the Minikube context.
* Helm (used to install the k6 Operator).

## 7. Installation method
After cloning the repository, prepare the local environment variables.

1. **Configure environment variables:**
   Copy the example environment file and set your `GOOGLE_API_KEY`:
   ```bash
   cp .env.example .env
   ```

## 8. Demo deployment steps
### 8.1. Configuration set-up
The deployment process involves starting the local Kubernetes cluster, building the necessary images inside it, and deploying the application containers.

1. **Start the Minikube cluster and deploy components:**
   ```bash
   ./k8s/start_minikube.sh
   ```
   *This script will start Minikube, build Docker images locally in its registry, install the k6 Operator via Helm, and apply all manifests from the `k8s/` directory.*

2. **Establish port forwarding:**
   Kubernetes `ClusterIP` services are not directly accessible from the host. Run these commands in separate terminal windows:
   ```bash
   # Access the Frontend Chat UI
   kubectl port-forward service/frontend-service 8081:8081

   # Access Grafana Dashboards
   kubectl port-forward service/grafana-service 3000:3000
   
   # Optional: Access the MCP Server directly
   kubectl port-forward service/mcp-service 8080:8080
   ```

3. **Verify the installation:**
   * **Web UI:** Open `http://localhost:8081` to interact with the AI Agent.
   * **Observability:** Open `http://localhost:3000` (default credentials: `admin/admin`) to view system metrics and dashboards.
   * **Automated Connectivity Test:**
     ```bash
     python mcp-server/test_mcp_connection_k8s_or_compose.py
     ```

### 8.2. Data preparation
Manual data preparation is not required. The Backend Service automatically seeds the SQLite database with a default product catalog (`backend/products.csv`) upon its first startup.

## 9. Demo description
### 9.1. Execution procedure

#### I. Functional Testing (Frontend)
1. Access the Chat UI at `http://localhost:8081`.
2. **Phase A: Cloud LLM (Gemini):**
   - Ensure the Gemini profile is selected.
   - **Prompt 1 (Product Discovery):** *"Show me available laptops"*
     - *Expected result:* The agent should quickly use the `list_products` tool and show various laptops including e.g. "Dellta Laptop Pro" and "Macrosoft Laptop Lite".
   - **Prompt 2 (Shipping):** *"How much would it cost to ship 2 Dellta Laptop Pro and 5 Macrosoft Laptop Lite?"*
     - *Expected result:* The agent should call `get_shipping_quote` and provide a cost estimate.
   - **Prompt 3 (Packaging):** *"How should I pack these products?"*
     - *Expected result:* The agent should call `optimize_packaging` and provide a box distribution strategy.
3. **Phase B: Local LLM (Ollama):**
   - Switch the profile to **Ollama** in the UI.
   - Run the same prompts as above.
   - **Important Note:** Local execution via Ollama might take significantly longer. Additionally, lighter models are generally "less intelligent" and may struggle with complex tool selection compared to Gemini.

#### II. Observability Baseline
1. Open Grafana at `http://localhost:3000`.
2. Navigate to the **Services Overview** dashboard.
3. Observe the baseline (idle) metrics for the Backend and MCP server.

#### III. Load Testing (k6)
Run the load tests using the provided script or individually via `kubectl`.

**To run all tests sequentially:**
```bash
./k6/run-all-tests.sh
```

**Individual tests (available in `k6/tests/scripts/`):**
- `connection-test.js`: Verifies the k6 client can establish a handshake with the MCP server.
- `validation-test.js`: Validates that the MCP server correctly handles tool discovery and JSON-RPC responses.
- `list-products-load-test.js`: High-frequency product searching.
- `shipping-quote-load-test.js`: Simulates external shipping provider API latency.
- `packaging-load-test.js`: Tests CPU-intensive optimization logic.
- `mixed-load-test.js`: A complex scenario combining all tools with ramping virtual users.

### 9.2. Results presentation

#### I. Frontend (Chat UI) Results
##### Gemini
Gemini quickly responded to all questions.

![Gemini Question 1 Part 1](docs/img/presentation/frontend/gemini_q1_1.png)
![Gemini Question 1 Part 2](docs/img/presentation/frontend/gemini_q1_2.png)
![Gemini Question 2](docs/img/presentation/frontend/gemini_q2.png)
![Gemini Question 3](docs/img/presentation/frontend/gemini_q3.png)

##### Ollama (qwen3.5:4b)
Local model (`qwen3.5:4b`) took a long time to answer the questions. First question alone took over 10 minutes to respond.

![Ollama Question 1 Part 1](docs/img/presentation/frontend/ollama_q1_1.png)
![Ollama Question 1 Part 2](docs/img/presentation/frontend/ollama_q1_2.png)
![Ollama Question 2](docs/img/presentation/frontend/ollama_q2.png)
![Ollama Question 3](docs/img/presentation/frontend/ollama_q3.png)

#### II. General System Metrics
After performing the tests, the **Services Overview** dashboard provides a high-level view of how the infrastructure handled the load.
- **Request Rate:** Shows the spikes in traffic for both REST (Backend) and MCP (FastMCP).
- **Latency (P95):** Shows the 95th percentile latency for both backend and MCP server.

![General Services Metrics](docs/img/presentation/grafana/grafana_3_services_after_tests.png)

#### III. k6 Performance Metrics
The **k6 Load Test** dashboard focuses on the client-side experience and protocol-level performance.
- **Virtual Users (VUs):** The number of concurrent agents simulated.
- **Throuput by Tool:** Shows the number of requests handled per second by each tool.
- **Latency by Tool (P95):** Shows the 95th percentile latency for each tool.
- **Iteration Duration:** Shows the duration of each test iteration.

![k6 Performance Metrics](docs/img/presentation/grafana/grafana_4_k6_all_after_tests.png)

#### IV. Test-by-Test Analysis
Below is a detailed breakdown of how specific tools behaved under load:

**1. List Products (Search Performance)**
This test simulates high-frequency product searching. As a read-only, lightweight operation, it exhibits the highest throughput and lowest latency.

```text
  █ THRESHOLDS 

    checks
    ✓ 'rate>0.95' rate=100.00%

    iteration_duration
    ✓ 'p(95)<3000' p(95)=1.17s


  █ TOTAL RESULTS 

    checks_total.......: 854     14.033951/s
    checks_succeeded...: 100.00% 854 out of 854
    checks_failed......: 0.00%   0 out of 854

    ✓ list_products returns valid response
```

![List Products Results](docs/img/presentation/grafana/grafana_7_k6_products_list.png)

**2. Shipping Quotes (External API Simulation)**
This scenario tests the system's ability to handle simulated external API latency. The backend interacts with four virtual shipping providers, each introducing randomized network-like delays.

```text
  █ THRESHOLDS 

    checks
    ✓ 'rate>0.95' rate=100.00%

    iteration_duration
    ✓ 'p(95)<8000' p(95)=3.58s


  █ TOTAL RESULTS 

    checks_total.......: 340     5.534576/s
    checks_succeeded...: 100.00% 340 out of 340
    checks_failed......: 0.00%   0 out of 340

    ✓ shipping quote returns valid response
```

![Shipping Quote Results](docs/img/presentation/grafana/grafana_8_k6_shipping_quote.png)

**3. Packaging Optimization (CPU Load)**
This test targets the most computationally expensive part of the system. The optimization algorithm includes an intentional CPU load, which, combined with high concurrency, results in increased latency and a slight drop in the success rate as the system reaches its resource limits.

```text
  █ THRESHOLDS 

    checks
    ✓ 'rate>0.90' rate=96.41%

    iteration_duration
    ✓ 'p(95)<10000' p(95)=4.76s


  █ TOTAL RESULTS 

    checks_total.......: 279    4.434887/s
    checks_succeeded...: 96.41% 269 out of 279
    checks_failed......: 3.58%  10 out of 279

    ✗ packaging returns valid response
      ↳  96% — ✓ 269 / ✗ 10
```

![Packaging Results](docs/img/presentation/grafana/grafana_9_k6_packaging.png)

**4. Mixed Load (System Resilience)**
This final test combines all three tools (Product List, Shipping Quote, Packaging) in a single scenario with ramping virtual users. It demonstrates how the system handles a realistic, heterogeneous workload. The results show a 99.46% overall success rate, with the minor failures occurring exclusively in the resource-heavy packaging tool.

```text
  █ THRESHOLDS 

    checks
    ✓ 'rate>0.95' rate=99.46%

    iteration_duration
    ✓ 'p(95)<10000' p(95)=5.78s


  █ TOTAL RESULTS 

    checks_total.......: 1308   10.790427/s
    checks_succeeded...: 99.46% 1301 out of 1308
    checks_failed......: 0.53%  7 out of 1308

    ✓ list products returns valid response
    ✓ shipping quote returns valid response
    ✗ optimize packaging returns valid response
      ↳  98% — ✓ 429 / ✗ 7
```

![Mixed Load Results](docs/img/presentation/grafana/grafana_10_k6_mixed.png)

## 10. Summary

This project successfully demonstrated the application of load testing to Model Context Protocol (MCP) servers using the `xk6-mcp` extension. By simulating realistic interactions between AI agents and backend services, we validated the viability of k6 for evaluating tool-calling performance under stress.

The implemented architecture showcased a robust, observable microservices environment deployed on Kubernetes. It seamlessly integrated modern AI orchestration tools (LangChain, Ollama, Gemini) with a functional web backend (FastAPI, SQLite) and a user-friendly interface (Chainlit).

Furthermore, the comprehensive observability stack—powered by OpenTelemetry, Prometheus, and Grafana—provided actionable insights into system behavior. The collected metrics confirmed overall system stability during load tests while successfully identifying minor bottlenecks (such as a ~2% failure rate in complex packaging optimization requests), highlighting the effectiveness and necessity of this testing approach for AI-integrated applications.

## 11. References

* [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro)
* [xk6-mcp Extension](https://github.com/grafana/xk6-mcp)
* [Grafana k6](https://k6.io/)
* [OpenTelemetry](https://opentelemetry.io/)
* [Prometheus](https://prometheus.io/)
* [Grafana](https://grafana.com/)
* [Chainlit](https://docs.chainlit.io/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [LangChain](https://python.langchain.com/)
* [Ollama](https://ollama.com/)
* [Kubernetes](https://kubernetes.io/)
