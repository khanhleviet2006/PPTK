import tempfile
from src.pipeline import run
from scripts.verify_outputs import verify

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        run(d, synthetic=True, n=960)
        verify(d)
        run(d, synthetic=True, n=960)  # resume must not re-access final test
        verify(d)
