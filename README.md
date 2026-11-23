# EnterpriseOps AI

EnterpriseOps AI is an AI-assisted operations workspace for
investigating order-fulfillment issues. It combines a React frontend,
FastAPI, Gemini-backed planning, LangGraph orchestration, and PostgreSQL
persistence.

> **Current scope:** workflows investigate operational records and
> produce recommendations. They do not modify orders, reserve or
> transfer stock, create purchase orders, or execute fulfillment
> actions. Approval decisions are recorded but do not trigger execution.

## Architecture

``` mermaid
flowchart LR
    U[Operator] --> FE[React + Vite]
    FE --> API[FastAPI]
    API --> TS[Task Service]
    TS --> LG[LangGraph]
    LG --> OR[Orchestrator]
    OR --> GM[Gemini]
    LG --> OA[Order Agent]
    LG --> IA[Inventory Agent]
    LG --> PA[Procurement Agent]
    LG --> FA[Fulfillment Evaluator]
    LG --> VA[Verification Agent]
    OA --> DB[(PostgreSQL)]
    IA --> DB
    PA --> DB
    FA --> DB
    VA --> DB
    TS --> DB
    LG --> CP[(LangGraph Checkpoints)]
```

### Task lifecycle

``` mermaid
sequenceDiagram
    actor Operator
    participant UI as React UI
    participant API as FastAPI
    participant S as Task Service
    participant G as LangGraph
    participant A as Specialist Agents
    participant DB as PostgreSQL
    Operator->>UI: Submit objective
    UI->>API: POST /api/tasks
    API->>S: Validate and create task
    S->>DB: Persist task
    S->>G: Invoke workflow
    G->>A: Run planned investigations
    A->>DB: Read operational records
    A-->>G: Return findings
    G->>DB: Persist execution data/checkpoints
    G-->>S: Return final report
    S->>DB: Update task and report
    S-->>UI: Return task response
```

Task submission is synchronous. The graph executes eligible plan steps
sequentially; independent steps are not currently parallelized.

## Agents

  -----------------------------------------------------------------------
  Agent/component                     Responsibility
  ----------------------------------- -----------------------------------
  Orchestrator                        Interprets objectives and creates
                                      validated execution plans

  Order                               Retrieves order details and line
                                      items

  Inventory                           Checks stock across active
                                      warehouses

  Procurement                         Investigates supplier offers and
                                      purchasing options

  Fulfillment                         Produces a read-only allocation and
                                      fulfillment recommendation

  Verification                        Independently checks
                                      recommendations against current
                                      records
  -----------------------------------------------------------------------

The workflow persists tasks, agent runs, messages, audit events,
approvals, and LangGraph checkpoints in PostgreSQL. Approval requests
explicitly set `execution_enabled: false`.

## Repository layout

``` text
.
├── backend/
│   ├── app/
│   │   ├── agents/       # Agent implementations and graph
│   │   ├── api/routes/   # Task and approval endpoints
│   │   ├── db/models/    # SQLModel database models
│   │   ├── schemas/      # API and workflow schemas
│   │   ├── services/     # Task execution and persistence
│   │   └── main.py
│   ├── migrations/
│   ├── scripts/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── styles/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
├── infrastructure/
│   └── docker-compose.yml
├── alembic.ini
└── README.md
```

## Technology

-   **Frontend:** React, Vite, React Router
-   **Backend:** Python, FastAPI, SQLModel
-   **Orchestration:** LangGraph
-   **Model provider:** Google Gemini
-   **Database and migrations:** PostgreSQL, Alembic

## Requirements

-   Python 3.11+
-   PostgreSQL 16
-   Node.js and npm
-   Gemini API key
-   Docker Compose (optional, for local PostgreSQL)

## Local setup

Run commands from the repository root unless stated otherwise.

### 1. Configure environment

Create `.env` from `.env.example`. Set `GEMINI_API_KEY` and
`DATABASE_URL`. The Compose service also requires:

``` dotenv
POSTGRES_DB=enterpriseops
POSTGRES_USER=enterpriseops
POSTGRES_PASSWORD=enterpriseops_dev
```

These are development credentials. Keep `.env` private and out of
version control.

### 2. Start PostgreSQL

``` bash
docker compose -f infrastructure/docker-compose.yml up -d postgres
```

Wait for the database health check to pass.

### 3. Install backend dependencies and migrate

``` bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
alembic upgrade head
```

### 4. Seed development records

``` bash
PYTHONPATH=backend python backend/scripts/seed_dev_user.py
PYTHONPATH=backend python backend/scripts/seed_dev_approver.py
PYTHONPATH=backend python backend/scripts/seed_orders.py
PYTHONPATH=backend python backend/scripts/seed_inventory.py
PYTHONPATH=backend python backend/scripts/seed_suppliers.py
```

Sample data includes order `ORD-1042` and products `SKU-1001` and
`SKU-1002`.

### 5. Install frontend dependencies

``` bash
cd frontend
npm install
```

## Run locally

Start the backend from the repository root:

``` bash
source .venv/bin/activate
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

Start the frontend in another terminal:

``` bash
cd frontend
npm run dev
```

Open <http://localhost:5173>. FastAPI runs at <http://localhost:8000>;
interactive API documentation is at `/docs`, and database health is
exposed at `/health`.

During development, Vite proxies `/api/*` and `/health` to port `8000`.

## API reference

  -----------------------------------------------------------------------------------------
  Method                  Endpoint                                  Description
  ----------------------- ----------------------------------------- -----------------------
  `GET`                   `/`                                       API identity

  `GET`                   `/health`                                 Database connectivity

  `POST`                  `/api/tasks`                              Create and
                                                                    synchronously execute a
                                                                    task

  `GET`                   `/api/tasks/{task_id}`                    Retrieve a task

  `GET`                   `/api/tasks/{task_id}/report`             Retrieve its final
                                                                    report

  `GET`                   `/api/approvals`                          List pending approvals

  `GET`                   `/api/approvals/{approval_id}`            Retrieve an approval

  `POST`                  `/api/approvals/{approval_id}/decision`   Record approval or
                                                                    rejection
  -----------------------------------------------------------------------------------------

### Create a task

The current workflow requires an order number in the objective or
`input_context.order_number`. The objective must contain 10--2,000
characters. Priority values are `low`, `normal`, `high`, or `critical`.

``` bash
curl -X POST http://localhost:8000/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "objective": "Investigate why order ORD-1042 has not shipped and recommend a resolution.",
    "priority": "high",
    "input_context": {}
  }'
```

The response includes the task UUID, task key, status, timestamps, input
context, and final report. Workflow execution finishes before the
response is returned.

### Review an approval

``` bash
curl -X POST http://localhost:8000/api/approvals/<approval-uuid>/decision \
  -H 'Content-Type: application/json' \
  -d '{
    "decision": "approved",
    "reviewer_comment": "Reviewed the recommendation."
  }'
```

Use `rejected` to reject. The decision and audit details are persisted,
but the proposed action is not executed and the workflow is not resumed.

## Data model

``` mermaid
erDiagram
    USER ||--o{ OPERATIONAL_TASK : creates
    OPERATIONAL_TASK ||--o{ AGENT_RUN : contains
    OPERATIONAL_TASK ||--o{ APPROVAL_REQUEST : may_require
    OPERATIONAL_TASK ||--o{ AUDIT_LOG : records
    AGENT_RUN ||--o{ AGENT_MESSAGE : emits
    ORDER ||--|{ ORDER_ITEM : contains
    WAREHOUSE ||--o{ INVENTORY : stores
    SUPPLIER ||--o{ SUPPLIER_PRODUCT : offers
    PURCHASE_ORDER ||--|{ PURCHASE_ORDER_ITEM : contains
```

The schema covers users, tasks, agent execution records, approvals,
audit logs, orders and line items, warehouses and inventory, suppliers
and offers, and purchase orders. Structured workflow data is stored in
JSON/JSONB fields where appropriate.

## Configuration

  Variable                  Purpose
  ------------------------- ------------------------------
  `DATABASE_URL`            PostgreSQL connection string
  `GEMINI_API_KEY`          Google GenAI credential
  `GEMINI_ROUTINE_MODEL`    Routine model selection
  `GEMINI_COMPLEX_MODEL`    Complex model selection
  `GEMINI_FALLBACK_MODEL`   Fallback model selection
  `APP_NAME`                FastAPI application title
  `APP_ENV`, `DEBUG`        Application settings
  `VITE_API_URL`            Optional frontend API origin

The model router supports fallback models for provider errors. Model
identifiers must be available to the configured Gemini account.

## Checks

``` bash
# Frontend build
cd frontend
npm run build

# Backend agent tests
cd ..
PYTHONPATH=backend pytest backend/scripts/test_order_agent.py backend/scripts/test_inventory_agent.py backend/scripts/test_procurement_agent.py

# Workflow and model-router checks
PYTHONPATH=backend python backend/scripts/test_graph.py
PYTHONPATH=backend python backend/scripts/test_model_router.py
```

Backend checks may require PostgreSQL, seeded records, and a valid
Gemini API key.

## Current limitations

-   Agents are read-only: no stock reservation, transfer, order update,
    purchase-order creation, or fulfillment execution.
-   Approval decisions are recorded but do not resume workflows or
    authorize operational actions.
-   Task submission is synchronous; no background worker or asynchronous
    job API is present.
-   There is no task-list, cancellation, retry/recovery, or WebSocket
    endpoint.
-   Plan steps execute sequentially rather than concurrently.
-   Business pages for orders, inventory, procurement, and agent
    registry use sample records; corresponding live list/mutation APIs
    are not exposed.
-   Task history is retained in browser storage because the backend has
    no task-list endpoint.
-   Authentication, role-based API authorization, and multi-tenant
    access controls are not implemented. Development routes use fixed
    operator/approver identities.
-   The Vite proxy is development-only. Deployment requires an API
    origin or reverse proxy and appropriate CORS configuration.

## Troubleshooting

  -----------------------------------------------------------------------
  Symptom                             Check
  ----------------------------------- -----------------------------------
  Frontend cannot reach API           Confirm FastAPI is running on port
                                      `8000`; check `/health`; restart
                                      Vite after proxy changes

  `/health` returns `503`             Check PostgreSQL, `DATABASE_URL`,
                                      and migrations

  Task reports missing order number   Include an existing order such as
                                      `ORD-1042` in the objective or
                                      `input_context.order_number`

  Task fails before planning          Check the operator seed, database
                                      records, Gemini key, and model
                                      configuration

  Approval decision returns `403`     Run `seed_dev_approver.py` against
                                      the configured database

  Compose cannot find PostgreSQL      Add the three `POSTGRES_*`
  variables                           variables to `.env`

  Frontend renders blank              Inspect the browser console and
                                      Vite terminal
  -----------------------------------------------------------------------
