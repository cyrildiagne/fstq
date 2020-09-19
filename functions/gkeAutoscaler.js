const functions = require('firebase-functions')
const { Collections } = require('./types')

// The Firebase Admin SDK to access Cloud Firestore.
// const admin = require('firebase-admin')

// Get a db handle.
// const db = admin.firestore()

// config must be set before deploying the function
// https://firebase.google.com/docs/functions/config-env#use_environment_configuration_to_initialize_a_module
// const queue = functions.config().queue

// console.log(queue)

const metricsCol = `${Collections.ROOT}/{queue}/${Collections.METADATA}/metrics`
exports.gkeAutoscaler = functions.firestore
  .document(metricsCol)
  .onUpdate((change, context) => {
    // Get metrics
    const { numQueued, numProcessed } = change.after.data()
    console.log(numQueued, numProcessed)

    // In the emulator, params is filled with undefined objects so we get
    // the queue name from the resource path.
    const queue = context.params.queue || context.resource.split('/')[6]
    console.log(queue)

    // Get some refs from firestore.
    // const queueRef = db.collection(Collections.ROOT).doc(queue)
    // const metricsRef = queueRef.collection(Collections.METADATA).doc('metrics')

    // TODO: get the current maxBatchSize value on gke
    // TODO: get the current maxWorkers value on gke
    // TODO: compute a baseline autoscaling target, eg: t = min(ql / mb, mw)
    // TODO: scale the deployment to value t
    // TODO: scale the nodepool size to value t
    return true
  })
