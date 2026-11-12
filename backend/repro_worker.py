import os
from pathlib import Path

from app import models
from app.database import Base, engine
from app.generators import seed_data

seed_data.EXPORT_DIR = Path(os.environ["REPRO_EXPORT_DIR"])
Base.metadata.create_all(bind=engine)

seed_data.generate_data(
    counts=seed_data.STARTER_COUNTS,
    reset=False,
    seed=20261022,
)

engine.dispose()
print("GENERATION COMPLETE:", seed_data.EXPORT_DIR)
