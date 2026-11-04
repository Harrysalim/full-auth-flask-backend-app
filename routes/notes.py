from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session
from marshmallow import ValidationError

from extensions import db
from models import Note, User
from schemas.note_schema import note_schema

notes_bp = Blueprint("notes", __name__)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return jsonify(error="Authentication required."), 401
        user = db.session.get(User, user_id)
        if user is None:
            session.clear()
            return jsonify(error="Authentication required."), 401
        user = db.session.get(User, user_id)
        if user is None:
            session.clear()
            return jsonify(error="Authentication required."), 401
        request.current_user = user
        return view(*args, **kwargs)
    return wrapped


def _validated_note_data(partial=False):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a JSON object.")
    if partial:
        return note_schema.load_update(body)
    return note_schema.load_create(body)


@notes_bp.get("/notes")
@login_required
def index():
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)
    except(TypeError, ValueError):
        return jsonify(error="page and per_page must be integers."), 400

    
    if page < 1 or per_page < 1:
        return jsonify(error="page and per_page must be positive integers."), 400

    max_per_page = current_app.config.get("MAX_PER_PAGE", 100)
    per_page = min(per_page, max_per_page)

    pagination = (
        Note.query.filter_by(user_id=request.current_user.id)
        .order_by(Note.created_at.desc(), Note.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify(
        notes=[note.to_dict() for note in pagination.items],
        pagination={
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        },
    ), 200


@notes_bp.post("/notes")
@login_required
def create():
    try:
        data = _validated_note_data()
    except ValidationError as error:
        return jsonify(errors=error.messages), 400
    
    note = Note(
        title=data["title"].strip(),
        content=data["content"].strip(),
        user_id=request.current_user.id,
    )
    if not note.title or not note.content:
        return jsonify(error="Title and content cannot be blank."), 400

    db.session.add(note)
    db.session.commit()
    return jsonify(note=note.to_dict()), 201


@notes_bp.get("/notes/<int:note_id>")
@login_required
def show(note_id):
    note = Note.query.filter_by(id=note_id, user_id=request.current_user.id).first()
    if note is None:
        return jsonify(error="Note not found"), 404
    return jsonify(note=note.to_dict()), 200


@notes_bp.patch("/notes/<int:note_id>")
@login_required
def update(note_id):
    note = Note.query.filter_by(id=note_id, user_id=request.current_user.id).first()
    if note is None:
        return jsonify(error="Note not found."), 404
    
    try:
        data = _validated_note_data(partial=True)
    except ValidationError as error:
        return jsonify(errors=error.messages), 400
    
    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify(error="Title cannot be blank."), 400
        note.title = title
    if "content" in data:
        content = data["content"].strip()
        if not content:
            return jsonify(error="Content cannot be blank."), 400
        note.content = content
    
    db.session.commit()
    return jsonify(note=note.to_dict()), 200



@notes_bp.delete("/notes/<int:note_id>")
@login_required
def destroy(note_id):
    note = Note.query.filter_by(id=note_id, user_id=request.current_user.id).first()
    if note is None:
        return jsonify(error="Note not found."), 404
    
    db.session.delete(note)
    db.session.commit()
    return "", 204