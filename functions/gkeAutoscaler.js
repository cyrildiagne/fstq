const functions = require('firebase-functions')
const { Collections } = require('./types')

// config must be set before deploying the function
// https://firebase.google.com/docs/functions/config-env#use_environment_configuration_to_initialize_a_module
const queue = functions.config().queue
const queueCol = `${Collections.ROOT}/${queue}/${Collections.QUEUED}/{itemId}`

exports.gkeAutoscaler = functions.firestore
  .document(queueCol)
  .onCreate((snap, context) => {
    const itemId = context.params.itemId
    const itemData = snap.data()

    // TODO: get the current maxBatchSize value on gke
    // TODO: get the current maxWorkers value on gke
    // TODO: read the current queueLength metric on Firestore
    // TODO: compute a baseline autoscaling target, eg: t = min(ql / mb, mw)
    // TODO: scale the deployment to value t
    // TODO: scale the nodepool size to value t
  })
