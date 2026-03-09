from flask import jsonify


META_KEYS = {"success", "message", "error", "data"}


def success_response(data=None, message=None, status=200, **legacy_fields):
    payload = {"success": True, "data": data or {}}
    if message:
        payload["message"] = message
    if legacy_fields:
        payload.update(legacy_fields)
    return jsonify(payload), int(status)


def error_response(error, status=400, data=None, **legacy_fields):
    payload = {
        "success": False,
        "error": str(error or "Request failed"),
        "data": data or {},
    }
    payload["message"] = payload["error"]
    if legacy_fields:
        payload.update(legacy_fields)
    return jsonify(payload), int(status)


def normalize_payload_for_api(payload, status_code):
    if not isinstance(payload, dict):
        return payload

    normalized = dict(payload)

    if "success" not in normalized:
        normalized["success"] = int(status_code) < 400

    if normalized.get("success"):
        if "data" not in normalized:
            data = {
                key: value
                for key, value in normalized.items()
                if key not in META_KEYS
            }
            normalized["data"] = data
    else:
        if "error" not in normalized:
            normalized["error"] = str(normalized.get("message") or "Request failed")
        if "message" not in normalized:
            normalized["message"] = normalized["error"]
        if "data" not in normalized:
            data = {
                key: value
                for key, value in normalized.items()
                if key not in META_KEYS
            }
            normalized["data"] = data

    return normalized
