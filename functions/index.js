'use strict'

// The Firebase Admin SDK to access Cloud Firestore.
const admin = require('firebase-admin')
admin.initializeApp()

const push = require('./push')
exports.push = push.push

const gkeAutoscaler = require('./gkeAutoscaler')
exports.gkeAutoscaler = gkeAutoscaler.gkeAutoscaler
