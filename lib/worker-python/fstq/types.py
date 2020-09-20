from enum import Enum


class Collections():
    # Root collection name
    ROOT = 'fstq'
    # Queue collection name
    QUEUED = 'queued'
    # Results collection name
    RESULTS = 'results'
    # Metadata collection name
    METADATA = 'metadata'


class Status():
    # Item is queued waiting to be processed.
    QUEUED = 'queued'
    # Item has been processed successfully.
    COMPLETE = 'complete'
    # Item processing failed.
    FAILED = 'failed'


class Metrics():
    # Number of queued items.
    NUM_QUEUED = 'numQueued'
    # Number of processed items.
    NUM_PROCESSED = 'numProcessed'
    # Number of failed items.
    NUM_FAILED = 'numFailed'


class Autoscaler():
    # Max batch size.
    MAX_BATCH_SIZE = 'maxBatchSize'
    # Min number of workers.
    MIN_WORKERS = 'minWorkers'
    # Max number of workers.
    MAX_WORKERS = 'maxWorkers'


class Defaults():
    # Default zone for GKE
    ZONE = 'us-central1-a'
    # Default GKE cluster id
    CLUSTER_ID = 'fstq'