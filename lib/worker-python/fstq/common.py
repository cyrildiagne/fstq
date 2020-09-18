from enum import Enum


class Collections(str, Enum):
    # Root collection name
    ROOT = 'fstq'
    # Queue collection name
    QUEUED = 'queued'
    # Results collection name
    RESULTS = 'results'
    # Metadata collection name
    METADATA = 'metadata'


class Status(str, Enum):
    # Item is queued waiting to be processed.
    QUEUED = 'queued'
    # Item has been processed successfully.
    COMPLETE = 'complete'
    # Item processing failed.
    FAILED = 'failed'


class Metrics(str, Enum):
    # Number of queued items.
    NUM_QUEUED = 'numQueued'
    # Number of processed items.
    NUM_PROCESSED = 'numProcessed'
    # Number of failed items.
    NUM_FAILED = 'numFailed'