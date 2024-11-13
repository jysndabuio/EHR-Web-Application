import secrets

def generate_secret_key():
    return secrets.token_hex(24)

def save_to_env_file(secret_key):
    with open(".env", "a") as env_file:
        env_file.write(f"\nSECRET_KEY={secret_key}")

if __name__ == "__main__":
    key = generate_secret_key()
    save_to_env_file(key)
    print("SECRET_KEY generated and saved to .env file.")