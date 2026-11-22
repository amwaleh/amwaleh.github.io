import argparse
import shutil
from pathlib import Path

from check_site import PUBLIC_ASSETS, check_site


def main():
    parser = argparse.ArgumentParser(description="Export only the approved public profile assets.")
    parser.add_argument("source", type=Path, help="Local private profile directory; never committed.")
    args = parser.parse_args()
    destination = Path(__file__).resolve().parents[1]
    if args.source.resolve() == destination:
        parser.error("The source must be separate from the public repository.")
    for name in ("Career-Journey-2016-2026.html", *PUBLIC_ASSETS):
        if not (args.source / name).is_file():
            parser.error(f"Missing presentation asset: {name}")
    shutil.copyfile(args.source / "Career-Journey-2016-2026.html", destination / "index.html")
    for name in PUBLIC_ASSETS:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.source / name, target)
    check_site(destination)
    print("Exported public presentations only; private data and original reviews were not copied.")


if __name__ == "__main__":
    main()
