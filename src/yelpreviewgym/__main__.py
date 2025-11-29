"""
Entry point for YelpReviewGym Streamlit app.
Run with: uv run python -m yelpreviewgym
"""
import sys
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from yelpreviewgym.streamlit_app import main

if __name__ == "__main__":
    main()
