const functions = require('firebase-functions')
const { Collections } = require('./types')

// The Firebase Admin SDK to access Cloud Firestore.
const admin = require('firebase-admin')

// Get a db handle.
const db = admin.firestore()

// config must be set before deploying the function
// https://firebase.google.com/docs/functions/config-env#use_environment_configuration_to_initialize_a_module
// const queue = functions.config().queue

// console.log(queue)
// A cache object that stores GKE configs for each queue to avoid retrieving
// the data from Firestore on each metrics update.
const gkeMetadataCache = {}

const metricsCol = `${Collections.ROOT}/{queue}/${Collections.METADATA}/metrics`
exports.gkeAutoscaler = functions.firestore
  .document(metricsCol)
  .onUpdate(async (change, context) => {
    // In the emulator, params is filled with undefined objects so we get
    // the queue name from the resource path.
    const queue = context.params.queue || context.resource.split('/')[6]

    // Get gke autoscaling settings from the queue's GKE metadata.
    if (!gkeMetadataCache[queue]) {
      const queueRef = db.collection(Collections.ROOT).doc(queue)
      const gke = queueRef.collection(Collections.METADATA).doc('gke')
      gkeMetadataCache[queue] = (await gke.get()).data()
    }
    const { maxBatchSize, minWorkers, maxWorkers } = gkeMetadataCache[queue]
    // Compute a baseline autoscaling target
    // TODO: implement a smarter algorithm that takes into account the current
    // processing speed of the queue and expected instance boot time to avoid
    // allocating new instances that will be booted after the queue has finished
    // processing.
    const { numQueued } = change.after.data()
    let target = numQueued / maxBatchSize
    // Clamp final target within settings' values.
    target = Math.min(Math.max(minWorkers, Math.floor(target)), maxWorkers)
    console.log(target)
    // TODO: debounce actual changes push
    // TODO: scale the deployment to value target
    // TODO: scale the nodepool size to value target
    return true
  })
