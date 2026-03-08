import os

def replace_in_file(filepath, old_text, new_text):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_text in content:
        content = content.replace(old_text, new_text)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Refined {filepath}")

replace_in_file('app/templates/base.html', "session.get('role') == 'ADMIN'", "session.get('role') in ['ADMIN', 'STAFF']")
replace_in_file('app/controllers/dashboard.py', "if role != 'ADMIN':", "if role not in ['ADMIN', 'STAFF']:")

# For rev.author.role since it's an Enum object
replace_in_file('app/templates/product_detail.html', "rev.author.role == 'ADMIN'", "rev.author.role.name in ['ADMIN', 'STAFF']")
replace_in_file('app/templates/manage_reviews.html', "rev.author.role == 'ADMIN'", "rev.author.role.name in ['ADMIN', 'STAFF']")

print("Done refining roles.")
