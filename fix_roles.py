import os
import re

app_dir = 'app'

for root, _, files in os.walk(app_dir):
    for filename in files:
        if filename.endswith('.py') or filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = re.sub(r"==\s*'admin'", "== 'ADMIN'", content)
            new_content = new_content.replace('!= \'admin\'', "!= 'ADMIN'")
            new_content = new_content.replace('!= "admin"', "!= 'ADMIN'")
            new_content = new_content.replace('== "admin"', "== 'ADMIN'")

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

print("Done replacing.")
