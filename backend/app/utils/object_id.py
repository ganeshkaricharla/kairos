from bson import ObjectId


def to_str(oid: ObjectId) -> str:
    return str(oid)


def to_oid(s: str) -> ObjectId:
    return ObjectId(s)


def doc_id(doc: dict) -> dict:
    """Convert MongoDB _id to string id field."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc
