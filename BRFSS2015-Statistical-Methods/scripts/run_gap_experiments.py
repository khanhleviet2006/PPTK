import argparse
from src_extensions.runner import run

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data")
    p.add_argument("--out", default="runs/gap_development")
    p.add_argument("--profile", choices=["SMOKE", "QUICK", "STANDARD", "EXTENDED"], default="QUICK")
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--mode", choices=["binary", "core_three"], default="binary")
    p.add_argument("--max-experiments", type=int)
    run(**vars(p.parse_args()))
