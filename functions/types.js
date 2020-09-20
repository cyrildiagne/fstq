// Collections names
const Collections = {
  // Root collection name
  ROOT: 'fstq',
  // Queue collection name
  QUEUED: 'queued',
  // Results collection name
  RESULTS: 'results',
  // Results collection name
  METADATA: 'metadata',
}

// Possible item processing statuses
const Status = {
  // Item is queued waiting to be processed.
  QUEUED: 'queued',
  // Item has been processed successfully.
  COMPLETE: 'complete',
  // Item processing failed.
  FAILED: 'failed',
}

// Metrics
const Metrics = {
  // Items queued.
  NUM_QUEUED: 'numQueued',
  // Items processed.
  NUM_PROCESSED: 'numProcessed',
  // Items failed.
  NUM_FAILED: 'numFailed',
}

// Metadata
const Metadata = {
  // The metrics doc.
  METRICS: 'metrics',
  // The gke doc.
  GKE: 'gke',
}

// Cluster
const Cluster = {
  // Default cluster zone.
  DEFAULT_ZONE: 'us-central1-a',
  // Default cluster ID.
  DEFAULT_ID: 'fstq',
}

module.exports = {
  Collections,
  Cluster,
  Status,
  Metrics,
  Metadata,
}
