"""Location of the database directory, which lives outside this repository."""

import os
from pathlib import Path

# The database is shared with the frontend and kept out of git.
# Override with the PREMIER_DATABASE_DIR environment variable.
DATABASE_DIR = Path(os.environ.get("PREMIER_DATABASE_DIR", "../database"))
