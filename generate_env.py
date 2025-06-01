import secrets
from pathlib import Path

def generate_secret_key():
    return secrets.token_urlsafe(50)

def create_env_file():
    # Define the absolute path to the .env file in the script's directory
    env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        print(".env already exists. If you want to recreate it, please delete the file first.")
        return

    secret_key = generate_secret_key()
    env_content = f"""# Automatically generated .env file for local development

# Environment
DEBUG=True
ENV=development

# Django secret key
SECRET_KEY={secret_key}

# Allowed hosts (local only)
ALLOWED_HOSTS=localhost,127.0.0.1

# Trusted origins for CSRF (local React frontend)
CSRF_TRUSTED_ORIGINS=http://localhost:5173/

# Note: CORS_ALLOWED_ORIGINS belongs in settings.py, not here, but remember to configure it:
# CORS_ALLOWED_ORIGINS=http://localhost:5173/
"""

    # Save with explicit utf-8 encoding
    with env_path.open("w", encoding="utf-8") as f:
        f.write(env_content)

    print(f".env created successfully at {env_path} with configuration for local development.")

if __name__ == "__main__":
    create_env_file()