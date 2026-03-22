# K6 - Using K6 project for application testing

This project is part of the 'Environment of Services' course at AGH University of Krakow (summer semester, 2026).

Authors:
- Jakub Ciura ([@jciura](https://github.com/jciura)),
- Bernard Gawor ([@Gawor270](https://github.com/Gawor270)),
- Krzysztof Ligarski ([@kligarski](https://github.com/kligarski)),
- Łukasz Zegar ([@lvk4z](https://github.com/lvk4z)).

## 1. Introduction
## 2. Theoretical background and technology stack

## 2.1 Warstwa aplikacji

### 2.1.1 Streamlit
Pythonowy framework do budowania interaktywnych aplikacji webowych. W projekcie pełni rolę frontendowego interfejsu.

Zalety:
- Minimalna ilość kodu
- Obsługuje streaming tokenów z LLM, odpowiedzi pojawiają się stopniowo
- Alternatywy: **Chainlit** (stworzony specjalnie pod chatboty LLM)

### 2.1.2 FastAPI
Nowoczesny, wysokowydajny framework webowy dla Pythona oparty na standardzie ASGI. W projekcie pełni dwie role: backend aplikacji biznesowej (REST API) oraz warstwa transportowa dla serwera MCP (via FastMCP + SSE).

Zalety:
- Automatyczna dokumentacja OpenAPI
- Asynchroniczny, natywnie integruje się z OpenTelemetry (opentelemetry-instrumentation-fastapi) 

### 2.1.3 SQLite
Lekka, bezserwerowa relacyjna baza danych. Warstwa persystencji dla backendu, przechowuje dane domenowe (np. produkty w magazynie).

Zalety:
- Zero konfiguracji, pojedynczy plik, odpowiednie do demo
- W razie potrzeby łatwa migracja na inne bazy danych

---

## 2.2 AI i orkiestracja

### 2.2.1 LangChain
Framework do budowania aplikacji opartych na LLM. Działa jako orkiestrator agenta i klient MCP. Łączy model językowy z narzędziami udostępnianymi przez serwer MCP.

- Agenty w stylu ReAct: LLM iteracyjnie decyduje które narzędzie wywołać na podstawie opisu narzędzi z serwera MCP
- Pakiet **langchain-mcp-adapters** automatycznie konwertuje schematy MCP na obiekty narzędzi LangChain
- Łatwa zamiana LLM (Gemini, Ollama, OpenAI) przez jedną zmianę konfiguracji

### 2.2.2 LLM - Gemini API / Ollama

**Google Gemini API** - chmurowe modele językowe Google.

- Natywne wsparcie function/tool calling
- Duże okno kontekstu
- Dostęp przez SDK **google-generativeai**

**Ollama** - uruchamianie lokalnych modeli LLM. Opcjonalny backend dla środowisk offline lub prywatnych.

- Pełna prywatność, brak kosztów API
- Modele: Llama 3, Mistral, Phi-3
- Interfejs kompatybilny z OpenAI SDK

### 2.2.3 FastMCP
Biblioteka Pythona upraszczająca budowanie serwerów MCP. 

- Narzędzie definiuje się jednym dekoratorem **@mcp.tool()** na zwykłej funkcji Pythona 
- Montując FastMCP wewnątrz FastAPI, cały ruch HTTP (w tym wiadomości protokołu MCP) przechodzi przez middleware FastAPI
- Protokół MCP definiuje ustandaryzowany interfejs dla listowania narzędzi i ich wykonywania czyli dokładnie to, co atakują skrypty testowe k6

---

## 2.3 Testowanie

### 2.3.1 Grafana k6
Open-source'owe narzędzie do testów obciążeniowych i wydajnościowych napisane w Go, ze skryptami testowymi w JavaScript. Zaprojektowane do osadzenia w pipeline'ach CI/CD, natywnie integruje się ze stackiem observability Grafany.

- Wirtualni użytkownicy (VU) - współbieżne goroutines, każda niezależnie wykonuje skrypt testowy, łatwe symulowanie dziesiątek równoległych agentów AI
- Wbudowane metryki: **http_req_duration**, **http_req_failed**, **iteration_duration**
- Eksport metryk do OpenTelemetry, Prometheus remote write

### 2.3.2 xk6-mcp
Rozszerzenie k6 dodające natywne możliwości klienta MCP do skryptów testowych. Pozwala komunikować się z serwerem MCP pełnym protokołem zamiast surowych wywołań HTTP.

- Bez xk6-mcp trzeba by ręcznie konstruować wiadomości JSON-RPC przez HTTP/SSE
- Pozwala walidować nie tylko latencję, ale też poprawność na poziomie protokołu: czy schematy narzędzi są prawidłowe, czy kody błędów są zwracane poprawnie

https://github.com/grafana/xk6-mcp

---

## 2.4 Stack observability

### 2.4.1 OpenTelemetry
Neutralny technologicznie framework CNCF do generowania, zbierania i eksportowania danych telemetrycznych (traces, metryki, logi). Centralny hub zbierający dane ze wszystkich komponentów.

### 2.4.2 Prometheus
Open-source'owy toolkit do monitoringu i alertowania. Przechowuje szeregi czasowe metryk i udostępnia PromQL do ich odpytywania.
Dwa tryby ingestii: Remote Write (kolektor pcha dane) lub Scrape (Prometheus odpytuje endpointy '/metrics')

### 2.4.3 Grafana
Open-source'owa platforma analityczna i wizualizacyjna. Łączy się z Prometheusem i renderuje konfigurowalne dashboardy.
Natywny plugin k6 dostarcza gotowy dashboard z wynikami testu (rozkład czasu odpowiedzi, liczba VU, współczynnik błędów)

---

## 2.5 Infrastruktura - Kubernetes

Platforma do orkiestracji kontenerów. Cały stack demo - aplikacja, serwer MCP, operator k6, kolektor OTel, Prometheus i Grafana uruchamiany jest na klastrze Kubernetes. 

**k6 Operator** pozwala deklarować test obciążeniowy jako manifest Kubernetes, testy mogą być wyzwalane przez pipeline CI przez 'kubectl apply'

---
## 3. Demo concept description
### 3.1. Application
### 3.2. Observability
### 3.3. Vizualization
## 4. Demo high level architecture
