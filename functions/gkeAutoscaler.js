const functions = require('firebase-functions')
const { Collections } = require('./types')
const container = require('@google-cloud/container')

// Create the Cluster Manager Client
const gke = new container.v1.ClusterManagerClient()

// The Firebase Admin SDK to access Cloud Firestore.
const admin = require('firebase-admin')

// Get a db handle.
const db = admin.firestore()

// The projectId is required to interact with the cluster.
const projectId = process.env.GCLOUD_PROJECT

// A cache object that stores GKE configs for each queue to avoid retrieving
// the data from Firestore on each metrics update.
const gkeMetadataCache = {}

const metricsCol = `${Collections.ROOT}/{queue}/${Collections.METADATA}/metrics`
exports.gkeAutoscaler = functions
 // We must give enough time for the resize operation to complete.
.runWith({ timeoutSeconds: 300 })
  .firestore.document(metricsCol)
  .onUpdate(async (change, context) => {
    // In the emulator, params is filled with undefined objects so we get
    // the queue name from the resource path.
    const queue = context.params.queue || context.resource.split('/')[6]
    const queueRef = db.collection(Collections.ROOT).doc(queue)

    // Wait until the cluster can be operated or this request becomes outdated.
    const lock = await getOpLock(queue, projectId)
    if (!lock) {
      console.log(`Resize outdated. Not applying value.`)
      return
    }
    console.log('Got lock!')

    // Get updated metrics values
    const { numQueued } = (
      await queueRef.collection(Collections.METADATA).doc('metrics').get()
    ).data()

    // Skip if values have changed while we got the lock since the function
    // will be called again with these updated values.
    if (numQueued !== change.after.data().numQueued) {
      console.log('Values outdated. Skipping.')
      return
    }

    // Get gke autoscaling settings from the queue's GKE metadata.
    if (!gkeMetadataCache[queue]) {
      const gke = queueRef.collection(Collections.METADATA).doc('gke')
      gkeMetadataCache[queue] = (await gke.get()).data()
    }
    const { maxBatchSize, minWorkers, maxWorkers } = gkeMetadataCache[queue]

    // Compute a baseline autoscaling target
    // TODO: Compute `numBatchPerInstance` based on the current processing speed
    // of the queue and expected instance boot time to avoid allocating new
    // instances that will finish booting after the queue has finished
    // processing.
    const numBatchPerInstance = 10
    let target = numQueued / (maxBatchSize * numBatchPerInstance)

    // Clamp final target within settings' values.
    target = Math.min(Math.max(minWorkers, Math.ceil(target)), maxWorkers)

    // Retrieve the node pool
    // https://googleapis.dev/nodejs/container/latest
    // https://cloud.google.com/kubernetes-engine/docs/reference/rest
    const nodePoolConfig = {
      projectId,
      clusterId: 'fstq',
      nodePoolId: queue,
      zone: 'us-central1-a',
    }
    const resp = await gke.getNodePool(nodePoolConfig)
    if (!resp[0]) {
      throw new Error(`Error retrieving node pool ${nodePoolConfig}`)
    }
    const nodePool = resp[0]

    console.log(
      `numQueued: ${numQueued},`,
      `maxBatchSize: ${maxBatchSize},`,
      `currentNodeCount: ${nodePool.initialNodeCount},`,
      `target: ${target}`
    )

    // Exit if target is same as current node count.
    if (target == nodePool.initialNodeCount) {
      return
    }

    // Scale the nodepool size to the value target
    try {
      console.log(`Applying the new pool size ${target}`)
      await gke.setNodePoolSize({
        ...nodePoolConfig,
        nodeCount: target,
      })
    } catch (e) {
      console.error('Error applying the new pool size')
    }

    // TODO: scale the deployment to the value target

    return true
  })

/**
 * Gets a resize operation lock.
 *
 * @return {Promise<Boolean>} A promise that resolves when no operation is
 * running on the cluster or when another lock has been requested.
 * The value returned is:
 *  - `true` when no operation is running AND no new lock has been requested
 *  - `false when a new lock has been requested
 */
async function getOpLock(queue, projectId) {
  return new Promise(async resolve => {
    // Get an initial timestamp.
    const timestamp = Date.now()
    // Get ref to the gke metadata document.
    const queueRef = db.collection(Collections.ROOT).doc(queue)
    const gkeRef = queueRef.collection(Collections.METADATA).doc('gke')
    // Start loop
    while (true) {
      // TODO: Perform operation as a transaction to avoid race conditions.
      // Get latestLockTimestamp on firestore.
      const lockTimestamp = (await gkeRef.get()).data().lockTimestamp
      // Check if up to date.
      if (lockTimestamp && lockTimestamp > timestamp) {
        resolve(false) // This request is outdated.
        return
      }
      // Set latestLockTimestamp on firestore.
      gkeRef.update({ lockTimestamp: timestamp })
      // Make sure no operation is running on the cluster otherwise wait 10s
      // And rerun the loop.
      const runningOp = await getRunningOperation(projectId)
      if (runningOp) {
        await sleep(10)
      } else {
        resolve(true)
        return
      }
    }
  })
}

/**
 * Get ongoing operation may block the rescaling.
 * @param {String} projectId The project id.
 */
async function getRunningOperation(projectId) {
  const ops = await gke.listOperations({
    projectId,
    zone: 'us-central1-a',
  })
  const runningOp = ops[0].operations.find(op => op.status === 'RUNNING')
  if (runningOp) {
    return runningOp.operationType
  }
}

/**
 * A simple async sleep
 * @param {Number} duration How long to sleep in second
 */
async function sleep(duration) {
  return new Promise(resolve => setTimeout(resolve, duration * 1000))
}
