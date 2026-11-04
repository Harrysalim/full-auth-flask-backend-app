from marshmallow import Schema, ValidationError, fields, validate

class NoteSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=160))
    content = fields.String(required=True, validate=validate.Length(min=1))

    def load_create(self, data):
        return self.data(data)

    def load_update(self, data):
        if not isinstance(data, dict) or not data:
            raise ValidationError("Request body must contain at least one field.")
        allowed = {"title", "content"}
        unknown = set(data) - allowed
        if unknown
            raise ValidationError({key: ["Unknown field."] for key in uknown})
        return self.load(data, partial=True)


note_schema = NoteSchema()