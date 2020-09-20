'use strict'

const { Collections, Status } = require('./types')

// The Cloud Functions for Firebase SDK to create Cloud Functions and setup
// triggers.
const functions = require('firebase-functions')

// Enable CORS.
const cors = require('cors')({ origin: true })

// The Firebase Admin SDK to access Cloud Firestore.
const admin = require('firebase-admin')

// Get a db handle.
const db = admin.firestore()

// Push HTTP Endpoint.
exports.push = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    try {
      // Grab the payload.
      const { payload, queue } = JSON.parse(req.body.data)
      const queueDoc = db.collection(Collections.ROOT).doc(queue)
      // Initialize a batch write
      const batch = db.batch()
      // Add empty result for the client to listen to.
      const resultsQueueRef = queueDoc.collection(Collections.RESULTS)
      const resultItemDoc = resultsQueueRef.doc()
      batch.set(resultItemDoc, {
        status: Status.QUEUED,
        dateAdded: admin.firestore.FieldValue.serverTimestamp(),
      })
      // Push queue item with payload.
      const queuedItemDoc = queueDoc
        .collection(Collections.QUEUED)
        .doc(resultItemDoc.id)
      batch.set(queuedItemDoc, {
        payload,
        dateAdded: admin.firestore.FieldValue.serverTimestamp(),
      })
      // Increment item queued counter.
      const metricsItemDoc = queueDoc
        .collection(Collections.METADATA)
        .doc('metrics')
      batch.update(metricsItemDoc, {
        numQueued: admin.firestore.FieldValue.increment(1),
      })
      // Commit writes.
      await batch.commit()

      // Send back a message that we've succesfully written the message.
      res.json({ data: { id: resultItemDoc.id, status: Status.QUEUED } })
    } catch (e) {
      console.log('error pushing')
      switch (e.code) {
        // NOT_FOUND is error code 5. For some reasons, the nodejs firebase
        // admin lib doesn't have proper types for errors yet:
        // https://github.com/googleapis/nodejs-firestore/issues/602
        case 5:
          res.status(404).json({ error: e })
          break
        default:
          res.status(500).json({ error: e })
          break
      }
    }
  })
})
