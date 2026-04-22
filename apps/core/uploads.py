MAX_UPLOAD_SIZE = 5 * 1024 * 1024

ALLOWED_IMAGE_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
}


def validate_uploaded_file(upload, *, allowed_types, label, max_size=MAX_UPLOAD_SIZE):
    if not upload:
        return

    if upload.size > max_size:
        raise ValueError(f'{label} deve ter no máximo 5 MB.')

    content_type = getattr(upload, 'content_type', '')
    if content_type not in allowed_types:
        raise ValueError(f'{label} deve estar em um formato permitido.')
