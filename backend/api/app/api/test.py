from core.security import get_password_hash

# Example password to hash
plain_password = "123456"

# Create a hash of the password
hashed_password = get_password_hash(plain_password)

print(f"Hashed password: {hashed_password}")
