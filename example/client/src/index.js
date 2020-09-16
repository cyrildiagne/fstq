import fstq from 'fstq'
import config from './firebase-config.js'

fstq.init(config)

async function demo() {
  try {
    // Add item to queue.
    const task = await fstq.push('my-queue', { text: 'hello world' })
    console.log(`Task '${task.id}' added. Waiting for completion...`)

    // Wait for item to be processed.
    const result = await task.result()
    console.log(`Task '${task.id}' complete! Result:`, result)
  } catch (e) {
    console.error(e)
  }
}

for (let i = 0; i < 5; i++) {
  demo()
}
