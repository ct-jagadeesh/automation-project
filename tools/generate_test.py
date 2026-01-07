# tools/generate_test.py
import sys
from utils.testcase_generator import generate_test_file

def main(argv):
    if len(argv) < 2:
        print("Usage: python -m tools.generate_test <url> [short description]")
        return 1
    url = argv[1]
    description = " ".join(argv[2:]) if len(argv) > 2 else None
    out = generate_test_file(url, description, out_dir="../tests")
    print("Generated test file:", out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
