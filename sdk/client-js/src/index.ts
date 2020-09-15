import * as firebase from "firebase/app"
import "firebase/firestore"
import "firebase/functions"

let app: firebase.app.App

interface FTQ {
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
    console.log('using dev functions')
    app.functions().useFunctionsEmulator('http://localhost:5001')
  }
}

async function push(queue: string, payload: any): Promise<Task> {
  // Push payload to queue using proxy.
  const pushFn = firebase.functions().httpsCallable('push')
  try {
    const resp = await pushFn(JSON.stringify({ queue, payload }))
    const { id, status } = resp.data

    // Listen for changes on returned document and wait for completion.
    const prom = new Promise((resolve, reject) => {
      const result = { text: 'complete' }
      resolve(result)
    })

    return { id, status, result: () => prom } as Task

  } catch (e) {
    throw e
  }
}

export default {
  init,
  push
} as FTQ
