### ✅ Architecture Strategy

**1. Project Layout**

```
tasklite/
├── main.py                     # FastAPI app entrypoint
├── config.py                  # Environment-specific config (gitignored)
├── routes/                    # Modular routers per feature/domain
│   └── tasks.py
├── data/
│   └── models/                # SQLAlchemy models
│       ├── task_model.py
│       ├── ...
├── schemas/                   # Pydantic request/response models
│   └── task_schema.py
├── services/                  # Business logic and database interaction
│   └── task_service.py
├── utils/                     # Formatters, helpers, etc.
│   └── formatters.py
├── Pipfile / Pipfile.lock     # Environment
├── README.md
```

**2. Layers**

* **routes/**: HTTP endpoints and routing logic.
* **schemas/**: Input validation and response models via Pydantic.
* **services/**: Core task logic—e.g., creating, updating, filtering.
* **models/**: Database structure via SQLAlchemy.
* **utils/**: Non-core helpers, formatting, etc.

**3. Key Conventions**

* Keep `main.py` clean—only app init and router registration.
* Every feature (e.g., task, tag) gets its own module set (`routes`, `schemas`, `services`).
* No database code in routes—delegated to services.
* Response formatting in `utils/formatters.py`.

---

### 📄 Team Policy: Backend Code Structure

**Document Title**: TaskLite Backend Organization Policy
**Version**: 1.0
**Audience**: All backend developers
**Last Updated**: \[Today’s Date]

#### Objective

Ensure clarity, modularity, and maintainability of the FastAPI backend through enforced structural conventions.

#### Directory Policy

1. **routes/**:

   * Contains all FastAPI route handlers.
   * Each file defines one `APIRouter`.
   * Routes must delegate logic to `services/`.

2. **services/**:

   * Implements business logic and DB transactions.
   * One file per domain (e.g., `task_service.py`).
   * No HTTP/JSON logic here—pure Python.

3. **schemas/**:

   * Defines all request and response models using Pydantic.
   * Split per domain, matching `routes/` and `services/`.

4. **models/**:

   * Pure SQLAlchemy models.
   * Only structural declarations—no logic.

5. **utils/**:

   * Contains reusable utilities: formatters, date handlers, etc.

6. **config.py**:

   * Local, gitignored.
   * Defines paths, secrets, database URIs.

#### Code Conventions

* All new commands go in `routes/` and link to `services/`.
* Route files must register their routers to `main.py`.
* Avoid putting logic in `main.py` or route handlers.
* All JSON validation must go through `schemas/`.

#### Enforcement

Code not conforming to this structure will be rejected in code review.
