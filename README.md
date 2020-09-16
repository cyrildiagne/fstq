# FSTQ

A fast and simple task queue for intensive workloads (ML, GPU, video
render...etc) using Firebase.

- **Transparently mix workers environments:** You can plug-in workers at any
  time and from anywhere to help process the queue: For instance you could start
  processing the queue with your home computer, add your work's computer at
  night and even add some GPUs from Colab during traffic bursts.
- **Autoscale remote GPU Workers:** You can also automatically scale a cluster of remote GPUs in Kubernetes based on the rate of items added/processed.
- **Dynamic batching:** Automatically and dynamically bulk items by batches
  to accelerate processing.
- **Only process once:** Guarantee that each item will only be processed once,
  even if multiple workers are listening to the queue at the same time.

# Getting Started

## 1. Setting up

1. Create a [Firebase]() project
2. Install and initialize the [Firebase tools](#)

   ```
   npm install -g firebase-tools
   firebase init
   ```

3. Install the fstq CLI and lib

   ```sh
   pip install fstq
   ```

4. Setup the Firebase project for FSTQ

   ```sh
   fstq init <firebase-project-id>
   ```

## 2. Add items to a processing queue

- Items can be added to a processing queue using the [javascript client lib](sdk/client-js).

  The example client [example/client/src/index.js]() shows how to add items to a queue we want to call `fstq-demo`:

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

  To run the example client:

  - `cd example/client`
  - Create a file `src/firebase-config.js` that exports your [firebase's web config]().
  - Run `yarn install`
  - Run `yarn run dev`
  - Navigate to [http://localhost:8080](http://localhost:8080)

## 3. Process the items with local or remote python workers

- Items can be pulled from the queue and processed using the [python worker lib](sdl/worker-python).

  The example worker [example/worker/main.py]() shows how to processes incoming items:

  ```python
  import fstq
  import model

  @fstq.run
  def process(items):
      results = [model(item['text']) for item in items]
      return [{'text': t} for t in results]
  ```

  To run the example worker:

  - Generate a credentials json file for your worker in [the firebase console](#)

  - <details><summary>Run locally</summary>
    <p>

    - Make sure you've installed and setup [Docker](#).

    - Start the example worker using Docker

      ```sh
      fstq run example/worker \
          --queue 'fstq-demo' \
          --credentials '/path/to/worker/credentials.json' \
          --max_batch_size 5
      ```

      </p>

  - <details><summary>Run in an autoscaling remote GPU cluster using GKE</summary>
    <p>

    - Make sure you've installed and setup [gcloud](#).

    - Deploy the worker's image and attach a gpu node pool to the queue

      ```sh
      fstq deploy_gke ./example/worker \
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
  | Processed:                   3045 items      |
  | Failed:                      20 items        |
  | Failed (last hour):          0 items         |
  |----------------------------------------------|
  | Incoming rate:               3 items/s       |
  | Processing rate:             2 items/s       |
  | Average latency:             2400 ms         |
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
