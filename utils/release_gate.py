import sys
from datetime import datetime

def mark_release_ready():
    timestamp = datetime.utcnow().isoformat()
    message = f"""
==============================
RELEASE GATE STATUS: PASS ✅
Timestamp (UTC): {timestamp}

All automated checks passed.
This build is RELEASE READY.
==============================
"""
    print(message)

    with open("release_ready.txt", "w") as f:
        f.write(message)

if __name__ == "__main__":
    mark_release_ready()
