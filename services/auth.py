from functools import wraps
from flask import request, jsonify
from firebase_admin import auth as fb_auth

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            decoded = fb_auth.verify_id_token(token)
            request.user = {"uid": decoded["uid"], "email": decoded.get("email")}
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return wrapper
