# Firestore Task Queue

- **Worker environment agnostic:** You can process the queue with on-premise
  GPUs and automatically scale-up remote GPU nodes if needed during traffic
  bursts.

### 1 - Add items to the queue using the [Javascript Client SDK](#):

```js
import ftq from "firestore-task-queue";
const queue = ftq.init("my-queue", FIREBASE_CLIENT_CONFIG);
```

```js
const task = await queue.push({ text: "hello world" });
const result = await task.result();
```

- `queue.push()` returns a `Task` object as soon as the item has been added to
  the queue (normally takes less than 100ms).

- `task.result()` provides an easy wait to wait for task completion which can
  take an undefined amount of time.

### 2 - Process queue items using the [Python Worker SDK](#):

```py
from ftq import ftq

def process(items):
    results = [x for x in items]
    return results

ftq.init(FIREBASE_CREDENTIALS_JSON, name='My Worker Name')
ftq.attach('my-queue', process, batch_size=5)
```
