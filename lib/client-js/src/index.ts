import * as firebase from 'firebase/app'
import 'firebase/firestore'
import 'firebase/functions'

let app: firebase.app.App

// Collections names
enum Collections {
  // Root collection name
  ROOT = 'fstq',
  // Queue collection name
  QUEUED = 'queued',
  // Results collection name
  RESULTS = 'results',
}

// Possible item processing statuses
enum Status {
  // Item is queued waiting to be processed.
  QUEUED = 'queued',
  // Item has been processed successfully.
  COMPLETE = 'complete',
  // Item processing failed.
  FAILED = 'failed',
}

// The Firebae functions.
enum API {
  Push = 'push',
}

interface FSTQ {
  init: (config: Object) => void
  push: (queueName: string, payload: any) => Promise<Task>
}

interface Task {
  id: string
  result: () => Promise<any>
}

async function init(config: any) {
  app = firebase.initializeApp(config)
  // Use the local functions in dev environment.
  if (process.env.NODE_ENV === 'development') {
    app.functions().useFunctionsEmulator('http://localhost:5001')
  }
}

async function push(queue: string, payload: any): Promise<Task> {
  // Push payload to queue using proxy.
  const pushFn = firebase.functions().httpsCallable(API.Push)
  try {
    const resp = await pushFn(JSON.stringify({ queue, payload }))
    const { id, status } = resp.data

    // Listen for changes on returned document and wait for completion.
    const prom = new Promise((resolve, reject) => {
      const doc = firebase
        .firestore()
        .collection(Collections.ROOT)
        .doc(queue)
        .collection(Collections.RESULTS)
        .doc(id)
      const unsub = doc.onSnapshot(snap => {
        const result = snap.data()
        switch (result.status) {
          case Status.COMPLETE:
            resolve(result)
            unsub()
            break
          case Status.FAILED:
            reject()
            unsub()
            break
        }
      })
    })

    return { id, status, result: () => prom } as Task
  } catch (e) {
    throw e
  }
}

export default {
  init,
  push,
} as FSTQ
