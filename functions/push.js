'use strict'

const { Collections, Status } = require('./types')

// The Cloud Functions for Firebase SDK to create Cloud Functions and setup
// triggers.
const functions = require('firebase-functions')

// Enable CORS.
const cors = require('cors')({ origin: true })

// The Firebase Admin SDK to access Cloud Firestore.
const admin = require('firebase-admin')
admin.initializeApp()

// Push HTTP Endpoint.
exports.push = functions.https.onRequest((req, res) => {
  cors(req, res, async () => {
    try {
      // Grab the payload.
      const { payload, queue } = JSON.parse(req.body.data)
      const queueDoc = admin.firestore().collection(Collections.ROOT).doc(queue)
      // Add empty result for the client to listen to.
      const resultItemDoc = await queueDoc.collection(Collections.RESULTS).add({
        status: Status.QUEUED,
        dateAdded: admin.firestore.FieldValue.serverTimestamp(),
      })
      // Push queue item with payload.
      const queuedItemDoc = queueDoc
        .collection(Collections.QUEUED)
        .doc(resultItemDoc.id)
      await queuedItemDoc.set({
        payload,
        dateAdded: admin.firestore.FieldValue.serverTimestamp(),
      })
      // Send back a message that we've succesfully written the message
      res.json({ data: { id: resultItemDoc.id, status: Status.QUEUED } })
    } catch (e) {
      console.log(e)
      res.status(500).json({ error: e })
    }
  })
})
