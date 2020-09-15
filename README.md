# Firestore Task Queue

- **Worker environment agnostic:** You can process the queue with on-premise
  GPUs and automatically scale-up remote GPU nodes if needed during traffic
  bursts.

### 1 - Add items to the queue using the [Javascript Client SDK](#):

First initialize the queue with a name and your firebase project client config:

```js
import ftq from 'firestore-task-queue'
const queue = ftq.init('my-queue', FIREBASE_CLIENT_CONFIG)
```

Then add items to the queue:

```js
const task = await ftq.push('my-queue', { text: 'hello world' })
const result = await task.result()
// Will print: {'text': 'dlrow olleh'}
```

- `queue.push()` returns a `Task` object as soon as the item has been added to
  the queue (normally takes a few milliseconds).

- `task.result()` provides an easy way to wait for task completion which can
  take an undefined amount of time.

### 2 - Process queue items using the [Python Worker SDK](#):

```py
import ftq

def reverse(text):
  return text[::-1]

def process(items):
    results = [reverse(item['text']) for item in items]
    return [{'text': t} for t in results]

ftq.start('my-queue', process)
```
