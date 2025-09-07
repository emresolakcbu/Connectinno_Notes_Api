from flask import Blueprint, request, jsonify
from .auth import require_auth
from firebase_admin import firestore as admin_fs

bp = Blueprint("notes", __name__, url_prefix="/notes")

def get_db():
    return admin_fs.client()

def _serialize_note(doc):
    data = doc.to_dict() or {}
    data["id"] = doc.id
    # Timestamp alanlarını ISO string yap
    for k in ["created_at", "updated_at"]:
        if k in data and data[k] is not None:
            try:
                data[k] = data[k].isoformat()
            except Exception:
                pass
    data.setdefault("kind", "text")
    data.setdefault("skin", "plain")
    return data

@bp.get("")
@require_auth
def list_notes():
    uid = request.user["uid"]
    docs = (
        get_db()
        .collection("notes")
        .where("userId", "==", uid)
        .order_by("updated_at", direction=admin_fs.Query.DESCENDING)
        .stream()
    )
    return jsonify([_serialize_note(d) for d in docs]), 200

@bp.post("")
@require_auth
def create_note():
    uid = request.user["uid"]
    body = request.get_json() or {}
    title = (body.get("title") or "").strip()
    content = (body.get("content") or "").strip()
    skin = (body.get("skin") or "plain").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    doc_ref = get_db().collection("notes").document()
    payload = {
        "userId": uid,
        "title": title,
        "content": content,
        "kind": "text",
        "skin": skin,
        "created_at": admin_fs.SERVER_TIMESTAMP,
        "updated_at": admin_fs.SERVER_TIMESTAMP,
    }
    doc_ref.set(payload)
    snap = doc_ref.get()
    return jsonify(_serialize_note(snap)), 201

@bp.put("/<note_id>")
@require_auth
def update_note(note_id):
    uid = request.user["uid"]
    ref = get_db().collection("notes").document(note_id)
    snap = ref.get()
    if not snap.exists:
        return jsonify({"error": "not found"}), 404
    if snap.to_dict().get("userId") != uid:
        return jsonify({"error": "forbidden"}), 403

    body = request.get_json() or {}
    updates = {}
    for k in ["title", "content", "skin"]:
        if k in body:
            updates[k] = (body.get(k) or "").strip()
    updates["kind"] = "text"
    updates["updated_at"] = admin_fs.SERVER_TIMESTAMP

    ref.update(updates)
    new_snap = ref.get()
    return jsonify(_serialize_note(new_snap)), 200

@bp.delete("/<note_id>")
@require_auth
def delete_note(note_id):
    uid = request.user["uid"]
    ref = get_db().collection("notes").document(note_id)
    snap = ref.get()
    if not snap.exists:
        return jsonify({"error": "not found"}), 404
    if snap.to_dict().get("userId") != uid:
        return jsonify({"error": "forbidden"}), 403
    ref.delete()
    return jsonify({"ok": True, "deletedId": note_id}), 200
