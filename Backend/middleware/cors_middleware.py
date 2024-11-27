# backend/middleware/cors_middleware.py
from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    """
    Thêm CORS middleware vào ứng dụng FastAPI.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5500"],  # Cho phép frontend tại http://127.0.0.1:5500
        allow_credentials=True,
        allow_methods=["*"],  # Cho phép tất cả các phương thức HTTP
        allow_headers=["*"],  # Cho phép tất cả các header
    )
