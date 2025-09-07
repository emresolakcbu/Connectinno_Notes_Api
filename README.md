Connectinno Notes — Backend API (Flask + Firebase)

A minimal, secure REST API for a notes app.
Auth is handled with Firebase Authentication (ID token), data is stored in Cloud Firestore via the Firebase Admin SDK.
Includes a small AI blueprint with stub endpoints (returns dummy data for now).

This backend implements the API part of the Connectinno Flutter Developer Case (notes CRUD, auth, offline-first on the client).

Tech stack

Python 3.10+

Flask (API)

firebase-admin (Auth verification + Firestore)

python-dotenv (env management)

Optional: Flask-Cors (if you’ll call this API from a web origin)

Project layout (relevant files):

.
├─ main.py                    # Flask app entrypoint
├─ services/
│  ├─ notes.py               # /notes CRUD (secured)
│  ├─ ai.py                  # /ai endpoints (stubbed)
│  └─ auth.py                # require_auth decorator (Firebase ID token)
├─ requirements.txt          # (recommended)
├─ .env.example              # (recommended)
└─ README.md                 # (this file)

Quick start
1) Create a Firebase project & service account key

In Firebase Console → Project settings → Service accounts → “Generate new private key”.

Save the downloaded JSON (e.g. serviceAccount.json) somewhere outside your repo if possible.

The service account must have access to Cloud Firestore.

2) Configure environment

Create a .env file at the project root (or set system env vars):

# .env
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/serviceAccount.json
PORT=8000


GOOGLE_APPLICATION_CREDENTIALS must point to the absolute path of the downloaded JSON.

3) Install & run
# create & activate a venv (recommended)
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# install deps
pip install -r requirements.txt
# If you don't have a requirements.txt yet:
# pip install flask python-dotenv firebase-admin google-cloud-firestore

# run
python main.py
# → Flask will start on http://localhost:8000 (unless PORT is overridden)


Health check:

curl http://localhost:8000/health
# {"status":"ok"}

Authentication

All /notes endpoints require a Firebase ID token in the Authorization header:

Authorization: Bearer <ID_TOKEN>


How to obtain <ID_TOKEN>:

Flutter app: await FirebaseAuth.instance.currentUser?.getIdToken()

Manual testing: sign in via your app and copy the token from logs, or use Firebase Auth REST endpoints to exchange email/password for an idToken.

If the header is missing/invalid, you’ll get:

{ "error": "Unauthorized" }      // 401


or

{ "error": "Invalid token" }     // 401

Endpoints
Health

GET /health → 200 OK

Notes (secured)

All notes are scoped per user (server reads uid from the verified ID token).

List notes

GET /notes

Response 200 — array of notes (sorted by updated_at desc):

[
  {
    "id": "docId123",
    "title": "My note",
    "content": "Body...",
    "kind": "text",
    "skin": "plain",
    "created_at": "2025-01-15T10:21:05.123456",
    "updated_at": "2025-01-16T08:09:02.000000"
  }
]

Create note

POST /notes
Body:

{
  "title": "Required",
  "content": "Optional text",
  "skin": "plain"      // one of: plain, yellow, pink, blue, purple, sepia, kraft
}


Responses:

201 Created → returns created note (with server timestamps)

400 Bad Request → { "error": "title is required" }

Update note

PUT /notes/<note_id>
Body (any subset is allowed; missing fields are kept as-is):

{ "title": "New title", "content": "New body", "skin": "yellow" }


Responses:

200 OK → updated note

403 Forbidden → note belongs to a different user

404 Not Found → note id doesn’t exist

Delete note

DELETE /notes/<note_id>

Responses:

200 OK → { "ok": true, "deletedId": "<note_id>" }

403 Forbidden / 404 Not Found (same semantics as above)

AI (stub, non-secured in app UX; secured by default if you keep require_auth)

The endpoints are wired and return dummy data for now; client shows a “Coming soon” toast.

POST /ai/suggest_title → { "title": "<first 20 chars>..." }

POST /ai/summarize → { "summary": "<first 50 chars>..." }

POST /ai/tags → { "tags": ["example","tags","from","ai"] }

All accept:

{ "content": "free text" }


You can later plug a real LLM here (OpenAI, Vertex AI, etc.). Keep the same payload/response shapes for a drop-in replacement.

Data model (Firestore)

Collection: notes
Each document:

Field	Type	Notes
userId	string	Owner’s Firebase uid
title	string	Required
content	string	Optional
kind	string	"text"
skin	string	`plain
created_at	timestamp	set by server
updated_at	timestamp	set by server

Server serializes timestamps to ISO 8601 strings in responses.

Error model

The API returns meaningful, compact JSON errors:

400 → { "error": "title is required" }

401 → { "error": "Unauthorized" } or { "error": "Invalid token" }

403 → { "error": "forbidden" }

404 → { "error": "not found" }

Network or unknown server errors will surface as standard HTTP errors.

cURL examples

Replace ID_TOKEN with a real Firebase ID token.

List:

curl -H "Authorization: Bearer ID_TOKEN" http://localhost:8000/notes


Create:

curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","content":"Body","skin":"plain"}'


Update:

curl -X PUT http://localhost:8000/notes/<id> \
  -H "Authorization: Bearer ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated"}'


Delete:

curl -X DELETE -H "Authorization: Bearer ID_TOKEN" \
  http://localhost:8000/notes/<id>


AI (stub):

curl -X POST http://localhost:8000/ai/summarize \
  -H "Content-Type: application/json" \
  -d '{"content":"Your text..."}'

Running with the Flutter app

In your Flutter app (development):

// di.dart
final String baseUrl = kReleaseMode
    ? 'https://<your-prod-host>'
    : 'http://10.0.2.2:8000'; // Android emulator → host machine

// ApiClient adds: Authorization: Bearer <idToken>


Ensure you’re logged in via FirebaseAuth before calling any /notes endpoint.

On logout, the app clears the local Drift cache and calls FirebaseAuth.signOut() (already implemented).

Optional: CORS

If you’ll call this API from a web origin (e.g., Flutter web), add CORS:

pip install flask-cors

# main.py
from flask_cors import CORS
# ...
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # restrict in production

Environment template (.env.example)
# Firebase
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/serviceAccount.json

# Server
PORT=8000

Production notes

Run behind a proper server (e.g., gunicorn or uvicorn with a WSGI adapter, plus a reverse proxy like Nginx).

Lock dependencies, rotate service account keys, restrict network egress as needed.

Consider rate limiting for AI endpoints once real models are connected.

License

MIT (or your choice)

Context

This backend accompanies a Flutter app that implements authentication, notes CRUD, offline-first local caching & sync, and a basic AI product vision, per the case requirements. 

Connectinno - Flutter Developer…

If anything is unclear or you want the README exported as a separate file (Markdown), tell me the filename and I’ll generate it.
