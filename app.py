from pathlib import Path
import runpy


runpy.run_path(Path(__file__).parent / "dashboard" / "app.py")
