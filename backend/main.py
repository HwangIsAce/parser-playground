"""Backend server entrypoint."""
import uvicorn

from api.app import create_app
from config import settings

app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
