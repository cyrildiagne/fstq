'use strict'

// The Cloud Functions for Firebase SDK to create Cloud Functions and setup
// triggers.
const functions = require('firebase-functions')

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
      // Push the task to Cloud Firestore using the Firebase Admin SDK.
      const doc = await admin
        .firestore()
        .collection('queues')
        .doc(queue)
        .collection('queued')
        .add({ payload, dateAdded: admin.firestore.FieldValue.serverTimestamp() })
      // Send back a message that we've succesfully written the message
      res.json({ data: { id: doc.id, status: 'added' } })
    } catch (e) {
      console.log(e)
      res.status(500).json({ error: e })
    }
  })
})
