"""Make scripts/ importable so the curriculum engine can be unit-tested.

curriculum.py is stdlib-only, so these tests run under plain pytest
(`uv run --with pytest pytest tests/`) without any notebook sandbox.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
