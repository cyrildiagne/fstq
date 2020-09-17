from enum import Enum

class Collections(str, Enum):
    # Root collection name
    ROOT = 'fstq'
    # Queue collection name
    QUEUED = 'queued'
    # Results collection name
    RESULTS = 'results'


class Status(str, Enum):
    # Item is queued waiting to be processed.
    QUEUED = 'queued'
    # Item has been processed successfully.
    COMPLETE = 'complete'
    # Item processing failed.
    FAILED = 'failed'