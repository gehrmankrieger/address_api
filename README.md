# Address API

A FastAPI service for Addresses. Users can create, read, update and delete addresses with coordinates, stored in SQLite, and search for addresses within a given distance of a point. The API is documented with FastAPI's built-in Swagger UI.

## Features

- Create, read, list (paginated), partially update and delete addresses
- Validation:
  - latitude −90..90 and longitude −180..180
  - required text fields can't be blank, and whitespace is trimmed
  - postal code format is checked
  - updates reject empty bodies and `null` on required fields
- Nearby search: addresses within `distance_km` of a point, sorted nearest first
- One log format for the app and the server; the level is set by `LOG_LEVEL`
- Settings from environment variables or a `.env` file
- Automated tests (pytest) and an end-to-end Postman collection

## Requirements

- Python 3.11+
- Git
- Optional: [Postman](https://www.postman.com/downloads/) or Node.js (for `newman`) to run the Postman collection

---

## End-to-end: from cloning to testing

Run all commands from the project root (the `address_api` folder) unless stated otherwise.

### 1. Clone the repository

```bash
git clone https://github.com/gehrmankrieger/address_api.git
cd address_api
```

### 2. Create and activate a virtual environment

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Git Bash)**
```bash
python -m venv .venv
source .venv/Scripts/activate
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your environment file

macOS / Linux / Git Bash:
```bash
cp .env.example .env
```
PowerShell:
```powershell
copy .env.example .env
```

The defaults work as they are. See [Configuration](#configuration) to change them.

### 5. Run the automated tests

```bash
pytest
```

Every test should pass. The tests use a fresh in-memory database, so they don't need the server running and don't touch `address_api.db`.

### 6. Start the API

```bash
uvicorn app.main:api --reload
```

You should see startup logs like:
```
... | INFO     | app.main | Starting: Address API v1.0.0
... | INFO     | app.main | DB ready: sqlite:///./address_api.db
... | INFO     | uvicorn.error | Application startup complete.
```

The SQLite file `address_api.db` is created automatically on first start.

### 7. Test manually in Swagger

Open **http://127.0.0.1:8000/docs**. For each row below:
1. Click the endpoint to expand it, then click **Try it out**.
2. Fill in the values and click **Execute**.
3. Compare the **Server response** with the expected result.

Run the rows in order. Rows 1 and 2 create the addresses that later rows use: Makati (call its id **A**) and Cebu (id **B**).

**Create** (`POST /addresses`)

| # | Request body | Expected |
|---|---|---|
| 1 | Makati, below | `201`. Note the `id` (A). `label` comes back trimmed as `"Office"` |
| 2 | Cebu, below | `201`. Note the `id` (B) |
| 3 | Makati body with `"latitude": 91` | `422`: latitude must be ≤ 90 |
| 4 | Makati body with `"longitude": -181` | `422`: longitude must be ≥ −180 |
| 5 | Makati body with `"city": "   "` | `422`: city too short (blank after trimming) |
| 6 | Makati body without `"street"` | `422`: field required |

Makati body:
```json
{
  "label": "  Office  ",
  "street": "Ayala Ave",
  "city": "Makati",
  "postal_code": "1226",
  "country": "Philippines",
  "latitude": 14.5547,
  "longitude": 121.0244
}
```

Cebu body (about 570 km from Manila):
```json
{
  "street": "Osmeña Blvd",
  "city": "Cebu City",
  "country": "Philippines",
  "latitude": 10.3157,
  "longitude": 123.8854
}
```

**Read**

| # | Endpoint | Input | Expected |
|---|---|---|---|
| 7 | `GET /addresses/{address_id}` | `address_id` = A | `200`, city `Makati` |
| 8 | `GET /addresses` | `skip` 0, `limit` 50 | `200`, a list containing A and B |

**Nearby search** (`GET /addresses/nearby`, search point Rizal Park: `latitude` 14.5831, `longitude` 120.9794)

| # | `distance_km` | Expected |
|---|---|---|
| 9 | `10` | `200`. A is listed with `distance_km` ≈ 5.78; B is not listed. Results are sorted nearest first |
| 10 | `1` | `200`, and A is not listed (it's ~5.8 km away) |
| 11 | `600` | `200`, both A and B listed, A first |
| 12 | `0` | `422`: must be greater than 0 |

**Update** (`PATCH /addresses/{address_id}`)

| # | Input | Expected |
|---|---|---|
| 13 | `address_id` = A, body `{"city": "Taguig"}` | `200`. City is `Taguig`, the other fields are unchanged and `updated_at` is newer |
| 14 | `address_id` = A, body `{"city": null}` | `422`: city cannot be null |
| 15 | `address_id` = A, body `{}` | `422`: provide at least one field |
| 16 | `address_id` = 999999, body `{"city": "X"}` | `404`: not found |

**Delete** (`DELETE /addresses/{address_id}`)

| # | Input | Expected |
|---|---|---|
| 17 | `address_id` = A | `204`, empty body |
| 18 | `GET /addresses/{address_id}` with A | `404` |
| 19 | `address_id` = A again | `404` |
| 20 | `address_id` = B | `204` (cleanup) |

While you test, the server terminal logs each create, update and delete, and a warning for each 404.

### 8. Run the end-to-end Postman collection (optional)

The collection runs the same 20 checks from step 7 automatically.

Leave the server running (step 6).

**With Postman**
1. **Import** → select `postman/address_api.postman_collection.json`
2. Right-click the **Address API** collection → **Run collection** → **Run**
3. All 20 requests should pass.

**From the command line** (needs Node.js)
```bash
npx newman run postman/address_api.postman_collection.json
```

The collection creates its own test data and deletes it at the end. It uses the variable `baseUrl` (default `http://127.0.0.1:8000`); edit it under the collection's **Variables** tab if the API runs elsewhere.

### 9. Stop the API

Press `Ctrl+C` in the server terminal. A `Shutting down` log line confirms a clean exit.

---

## Endpoints

| Method | Path | Description | Success |
|---|---|---|---|
| POST | `/addresses` | Create an address | 201 |
| GET | `/addresses?skip=0&limit=50` | List addresses (paginated, `limit` ≤ 100) | 200 |
| GET | `/addresses/nearby?latitude=&longitude=&distance_km=` | Addresses within `distance_km`, nearest first | 200 |
| GET | `/addresses/{id}` | Get one address | 200 |
| PATCH | `/addresses/{id}` | Update only the fields sent | 200 |
| DELETE | `/addresses/{id}` | Delete an address | 204 |
| GET | `/health` | Liveness check | 200 |

Invalid input returns `422` with details of each invalid field. An unknown id returns `404`.

## Configuration

These are set in `.env` or as environment variables.

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `Address API` | Title shown in the docs and logs |
| `DATABASE_URL` | `sqlite:///./address_api.db` | SQLAlchemy database URL |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Set `LOG_LEVEL=DEBUG` to also see how many candidates each nearby search checked.

## Project structure

```
address_api/
├── app/
│   ├── main.py              # App factory, lifespan (creates tables), DB error handler, /health
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   └── logging_config.py
│   ├── db.py                # Engine, session dependency, ORM Base
│   ├── models.py            # SQLAlchemy Address table
│   ├── schemas.py           # Pydantic request/response models and validation
│   ├── repository.py        # Database operations (no HTTP code)
│   ├── geo.py               # Haversine distance and bounding box (pure functions)
│   └── routers/
│       └── addresses.py     # HTTP endpoints
├── tests/                   # pytest suite (in-memory DB per test)
├── postman/                 # End-to-end Postman collection
├── .env.example
├── pyproject.toml           # Project metadata and pytest config
└── requirements.txt
```

## Design notes

- **Layers.** Routers handle HTTP only, the repository handles database work, and `geo.py` holds pure math. Each layer can be tested on its own.
- **Distance.** The haversine formula gives the great-circle distance on a sphere with mean Earth radius 6371 km. That is accurate to about 0.5%, which is plenty for an address book.
- **Nearby search in two passes.** SQLite has no built-in geo functions, so the search runs in two passes:
  1. An indexed bounding-box query (`latitude BETWEEN .. AND longitude BETWEEN ..`) quickly narrows the rows.
  2. The exact haversine distance removes the box's corners.

  Searches that reach a pole or cross the 180° meridian fall back to the full longitude range.
- **Sync endpoints.** The SQLite driver is synchronous, so the endpoints are plain `def`. FastAPI runs them in a thread pool, so they don't block the event loop.
- **Errors.** Unexpected database errors are logged in full but return a generic `500` to the client.
- **Tables** are created on startup with `create_all`. A production service would use migrations (Alembic) instead.
