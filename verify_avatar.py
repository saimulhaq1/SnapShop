from app.controllers.profile import get_gravatar_url
import hashlib

# Test Email
email = "test@example.com"
expected_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
expected_url = f"https://www.gravatar.com/avatar/{expected_hash}?d=identicon"

# Generate URL
generated_url = get_gravatar_url(email)

print(f"Email: {email}")
print(f"Expected URL: {expected_url}")
print(f"Generated URL: {generated_url}")

if generated_url == expected_url:
    print("SUCCESS: Gravatar URL logic is correct.")
else:
    print("FAILURE: Gravatar URL logic is incorrect.")

# Test Empty Email
empty_url = get_gravatar_url("")
print(f"Empty Email URL: {empty_url}")
