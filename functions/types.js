// Collections names
const Collections = {
  // Root collection name
  ROOT: 'fstq',
  // Queue collection name
  QUEUED: 'queued',
  // Results collection name
  RESULTS: 'results',
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

module.exports = {
  Collections,
  Status,
}
