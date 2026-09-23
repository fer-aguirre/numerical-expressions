"""Build the website: package the Python code as a wheel the browser can install.

    uv run python scripts/build_web.py           # build into web/dist
    uv run python scripts/build_web.py --serve   # build, then serve on http://localhost:8000
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
DIST = WEB / "dist"


def build() -> str:
    shutil.rmtree(DIST, ignore_errors=True)
    subprocess.run(["uv", "build", "--wheel", "--out-dir", str(DIST)], cwd=ROOT, check=True)
    wheel = next(DIST.glob("numerical_expressions-*.whl")).name
    # The page reads the wheel's name from here, so it never needs editing on a version bump.
    (DIST / "manifest.json").write_text(json.dumps({"wheel": wheel}) + "\n", encoding="utf-8")
    return wheel


def serve(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(WEB))
    with http.server.ThreadingHTTPServer(("localhost", port), handler) as server:
        print(f"Serving the website on http://localhost:{port} (Ctrl+C to stop)")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--serve", action="store_true", help="serve the website after building it")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    print("Built", build(), file=sys.stderr)
    if args.serve:
        serve(args.port)


if __name__ == "__main__":
    main()
