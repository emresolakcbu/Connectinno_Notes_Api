import os
from flask import Flask
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from services.notes import bp as notes_bp
from services.ai import bp as ai_bp

load_dotenv()

cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred, {
    "projectId": os.environ.get("FIREBASE_PROJECT_ID")
})

app = Flask(__name__)
app.register_blueprint(notes_bp)
app.register_blueprint(ai_bp)

@app.get("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", "8000")), debug=True)
