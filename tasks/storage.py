import os
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage


def upload_attachment(uploaded_file):
    """Use Supabase when configured, otherwise store locally for SQLite development."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    bucket = os.getenv("SUPABASE_BUCKET")
    if not all([supabase_url, supabase_key, bucket]):
        path = f"attachments/{uuid4()}-{Path(uploaded_file.name).name}"
        saved_path = default_storage.save(path, uploaded_file)
        return saved_path, uploaded_file.name

    from supabase import create_client

    path = f"tasks/{uuid4()}-{uploaded_file.name}"
    client = create_client(supabase_url, supabase_key)
    client.storage.from_(bucket).upload(
        path,
        uploaded_file.read(),
        {"content-type": uploaded_file.content_type or "application/octet-stream"},
    )
    return path, uploaded_file.name


def attachment_url(path):
    public_url = os.getenv("SUPABASE_PUBLIC_URL")
    if public_url and path:
        return f"{public_url.rstrip('/')}/{path}"
    if path:
        return f"{settings.MEDIA_URL.rstrip('/')}/{path}"
    return ""
