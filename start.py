"""Start locally or on Railway using its assigned PORT."""
import os
import uvicorn


def get_port():
    raw = os.environ.get('PORT', '8000')
    try:
        port = int(raw)
    except ValueError:
        raise ValueError('PORT must be an integer between 1 and 65535.') from None
    if not 1 <= port <= 65535:
        raise ValueError('PORT must be between 1 and 65535.')
    return port


if __name__ == '__main__':
    uvicorn.run(
        'server:app',
        host='0.0.0.0',
        port=get_port(),
        workers=1,
        timeout_graceful_shutdown=5,
    )
