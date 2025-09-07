# services/ai.py
from flask import Blueprint, request, jsonify

bp = Blueprint("ai", __name__, url_prefix="/ai")

@bp.post("/suggest_title")
def suggest_title():
    data = request.get_json(force=True)
    content = data.get("content", "")
    # şimdilik dummy cevap
    return jsonify({"title": content[:20] + "..."}), 200

@bp.post("/summarize")
def summarize():
    data = request.get_json(force=True)
    content = data.get("content", "")
    return jsonify({"summary": content[:50] + "..."}), 200

@bp.post("/tags")
def tags():
    data = request.get_json(force=True)
    content = data.get("content", "")
    return jsonify({"tags": ["example", "tags", "from", "ai"]}), 200
