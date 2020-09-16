'use strict'

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
      const queueDoc = admin.firestore().collection('queues').doc(queue)
      // Add empty result for the client to listen to.
      const doc = await queueDoc.collection('results').add({
        status: 'queued',
        dateAdded: admin.firestore.FieldValue.serverTimestamp(),
      })
      // Push queue item with payload.
      await queueDoc.collection('queued').doc(doc.id).set({
        payload,
        dateAdded: admin.firestore.FieldValue.serverTimestamp(),
      })
      // Send back a message that we've succesfully written the message
      res.json({ data: { id: doc.id, status: 'queued' } })
    } catch (e) {
      console.log(e)
      res.status(500).json({ error: e })
    }
  })
})
