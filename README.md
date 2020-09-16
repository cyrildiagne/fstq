# FSTQ

A fast and easy to use task queue for intensive workloads (ML, GPU, video
render...etc) using Firebase.

- **Transparently mix workers environments:** You can plug-in workers at any
  time and from anywhere to help process the queue: For instance you could start
  processing the queue with your home computer, add your work's computer at
  night and even add some GPUs from Colab during traffic bursts.
- **Autoscale remote GPU Workers:** automatically scale up a cluster of remote
  GPUs in Kubernetes based on the rate of items added/processed.
- **Dynamic batching:** Automatically and dynamically bulk items by batches
  to accelerate processing.
- **Only process once:** Guarantee that each item will only be processed once,
  even if multiple workers are listening to the queue at the same time.

# Getting Started

## 1. Create and configure a Firebase project

1. Create a [Firebase]() project
2. Install and initialize the [Firebase tools](#)

   ```
   npm install -g firebase-tools
   firebase init
   ```

3. Setup the Firebase project for FSTQ

   ```sh
   ./scripts/setup_firebase.sh
   ```

## 2. Add items to the queue

Items can be added to the queue using the [javascript client lib](sdk/client-js)

[example/client/src/index.js]() contains the client code adding items to the queue

```js
async function process() {
  const task = await fstq.push('fstq-demo', { text: 'hello world' })
  const result = await task.result()
  console.log(result)
}
for (let i = 0; i < 1000; i++) {
  process()
}
```

To run the example's client:

- `cd example/client`
- Create a file `src/firebase-config.js` that exports your [firebase's web config]().
- Run `yarn install`
- Run `yarn run dev`
- Navigate to [http://localhost:8080](http://localhost:8080)

## 3. Process the items with local or remote python workers

Items can be pulled and processed from the queue in workers using the [python worker lib](sdl/worker-python)

[example/worker/main.py]() contains the worker's code that processes incoming items:

```python
import fstq
import model

@fstq.run
def process(items):
    results = [model(item['text']) for item in items]
    return [{'text': t} for t in results]
```

To run example's worker:

- Generate a `firebase_credentials` json for your worker in
  [the firebase console](#)

- <details><summary>Start a worker locally</summary>
  <p>

  - Make sure you've installed and setup [Docker](#).

  - Start the example worker using Docker

    ```sh
    cd example/worker
    ../../scripts/run_locally.sh . \
        --queue 'fstq-demo' \
        --credentials '/path/to/worker/credentials.json' \
        --max_batch_size 5
    ```

    </p>

- <details><summary>Start an autoscaling remote cluster of GPU workers using GKE</summary>
  <p>

  - Make sure you've installed and setup [gcloud](#).

  - Deploy the worker's image and attach a gpu node pool to the queue

    ```sh
    cd example/worker
    ../../scripts/deploy_gke.sh . \
        --queue 'fstq-demo' \
        --credentials '/path/to/worker/credentials.json' \
        --max_batch_size 5 \
        --gpu nvidia-t4 \
        --min_workers 0 \
        --max_workers 5
    ```

    </p>

## 4. Monitor

- Track some key metrics with the `fstq monitor` command:

  ```sh
  fstq monitor 'fstq-demo'
  ```

  Output:

  ```
  Queue
  +----------------------------------------------+
  | Queued:                      52 items        |
  |----------------------------------------------|
  | Processed:                   3045 items      |
  |----------------------------------------------|
  | Failed:                      20 items        |
  | Failed (last hour):          0 items         |
  |----------------------------------------------|
  | Incoming rate:               3 items/s       |
  | Processing rate:             2 items/s       |
  |----------------------------------------------|
  | Average latency:             2400ms          |
  +----------------------------------------------+

  Local Workers:                 1
  +----------------------------------------------+
  | Home laptop                                  |
  |                                              |
  | Up time:                     22d 6h 32min    |
  | Status:                      PROCESSING      |
  | Avg time per item:           3456 ms         |
  | GPU Memory:                  24% (16.0 Gib)  |
  |----------------------------------------------|

  Remote Workers:               2/16
  |----------------------------------------------|
  | Remote #1 - Nvidia T4                        |
  |                                              |
  | Up time:                     2h 18min        |
  | Status:                      PROCESSING      |
  | Avg time per item:           2156 ms         |
  | GPU Memory:                  24% (16.0 Gib)  |
  |----------------------------------------------|
  | Remote #2 - Nvidia T4                        |
  |                                              |
  | Up time:                     18min           |
  | Status:                      PROCESSING      |
  | Avg time per item:           1956 ms         |
  | GPU Memory:                  24% (16.0 Gib)  |
  +----------------------------------------------+
  ```
