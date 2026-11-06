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
p.add_argument("--through", choices=STAGES, default="develop")
p.add_argument("--mode", choices=["binary", "core_three"], default="binary")
p.add_argument(
    "--final-evaluation",
    action="store_true",
    help="Explicit opt-in for frozen final-test evaluation",
)
if __name__ == "__main__":
    args = vars(p.parse_args())
    final = args.pop("final_evaluation")
    if args["through"] in {"evaluate", "report"} and not final:
        p.error(
            "--through evaluate/report requires --final-evaluation; development defaults to --through develop"
        )
    run(**args)
