# Import standard library modules
from enum import Enum


class LibrarianRewriteInstruction(Enum):
    # TODO: Add other instructions here later on; e.g. simpler, professional, etc.
    TAGLISH = "taglish"
    CEBUANO = "cebuano"
    THAI = "thai"


# Settings
TOP_K = 20
CHUNK_SIZE = 1500  # value from ingestion
