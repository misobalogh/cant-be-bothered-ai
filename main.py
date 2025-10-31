import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="ctranslate2")

from cant_be_bothered.cli import app  # noqa: E402

if __name__ == "__main__":
    app()
