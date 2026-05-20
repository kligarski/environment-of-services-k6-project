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
    *   `GET /products`: Provides product discovery with name filtering. Returns details like price, weight, and dimensions.
    *   `POST /shipping/quote`: Calculates shipping estimates. It simulates concurrent interactions with four different shipping providers' APIs, each with randomized network-like latency.
    *   `POST /packaging/optimize`: Implements a heuristic packaging algorithm. It calculates how to fit multiple items into standard box sizes and includes an artificial CPU-intensive load to simulate heavy computational tasks.
    *   **Data Persistence:** Uses a local **SQLite** database for storing product information.
*   **MCP Server (FastMCP):** Implements the Model Context Protocol and acts as a gateway for LLM Agents.
    *   **Transport:** Uses **Streamable HTTP**, allowing for both standard request-response and SSE-based notifications/streaming.
    *   **Tooling:** Exposes three main tools: `list_products`, `get_shipping_quote`, and `optimize_packaging`, which directly map to the backend's REST endpoints.

*   **OTel Collector:** Receives metrics from all components via OTLP/gRPC (port 4317) and forwards them to Prometheus using Remote Write.
*   **Prometheus:** Configured with `--web.enable-remote-write-receiver` to accept pushed metrics. No scrape targets — all data comes from the OTel Collector.
*   **Grafana:** Dashboards are auto-provisioned at startup via ConfigMaps. Two dashboards are available:
    *   **Services Overview** — backend and MCP server HTTP metrics (request rate, P95 latency).
    *   **k6 Load Test** — k6 test metrics (virtual users, MCP request rate and duration, iteration duration).

## 6. Environment configuration description
The primary demonstration environment is built around Kubernetes to allow for load testing and production environment simulation. 

Requirements for the local machine:
* An operating system with containerization support (Linux, macOS, or Windows with WSL2).
* Python 3.12+ environment (for running simple test scripts to verify the connection).
* Docker.
* Minikube and the `kubectl` tool configured to use the Minikube context.
* Helm (used to install the k6 Operator).

*(Note: While Kubernetes is the target environment, the repository also includes a Docker Compose configuration which can be optionally used for quick local development and debugging.)*

## 7. Installation method
The installation process involves starting the local Kubernetes cluster, building the necessary images inside it, and deploying the application containers.

1. Start the Minikube cluster and deploy the components using the provided automation script:
   ```bash
   ./k8s/start_minikube.sh
   ```
   *This script will start Minikube, build Docker images locally in its registry (including the custom k6+xk6-mcp image), install the k6 Operator via Helm, and apply all manifests from the `k8s/` directory.*
2. Kubernetes `ClusterIP` services are not directly accessible from the host. To access the MCP server, run port forwarding:
   ```bash
   kubectl port-forward service/mcp-service 8080:8080
   ```
3. To verify the installation, run the test script in a new terminal window:
   ```bash
   python mcp-server/test_mcp_connection_k8s_or_compose.py
   ```

## 8. Demo deployment steps:
### 8.1. Configuration set-up
WIP

### 8.2. Data preparation
WIP

## 9. Demo description
### 9.1. Execution procedure
WIP

### 9.2. Results presentation
<!-- All prompts used with AI models should be listed, screens from Grafana dashboard should be attached. -->
WIP

## 10. Summary
<!-- conclusions -->
WIP

## 11. References
WIP
