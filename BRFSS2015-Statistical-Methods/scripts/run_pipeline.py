import argparse
from src.pipeline import run, STAGES

p = argparse.ArgumentParser(description="BRFSS 2015 auditable research pipeline")
p.add_argument("--out", default="runs/synthetic")
p.add_argument("--data")
p.add_argument("--codebook")
p.add_argument("--synthetic", action="store_true")
p.add_argument("--n", type=int, default=960)
p.add_argument("--seed", type=int, default=2015)
p.add_argument("--profile", choices=["quick", "standard", "extended"], default="quick")
p.add_argument("--through", choices=STAGES, default="report")
p.add_argument("--mode", choices=["binary", "core_three"], default="binary")
if __name__ == "__main__":
    run(**vars(p.parse_args()))
