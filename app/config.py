import os

class Config:
    # MongoDB connection string
    MONGO_URI = "mongodb://localhost:27017/bus_ticket_booking"
    
    # Secret key for session security (use a fixed key instead of generating on every restart)
    SECRET_KEY = os.getenv("SECRET_KEY", "your-fixed-secret-key")  # Use env var or fixed key

    # 🔹 Session Configuration
    SESSION_TYPE = "filesystem"  # Stores session data in the filesystem
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True  # Encrypts session data for security
    SESSION_FILE_DIR = os.path.join(os.getcwd(), "flask_session")  # Optional: Custom session directory
