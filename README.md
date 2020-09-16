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

1. Install and initialize the [Firebase tools](#)

   ```
   npm install -g firebase-tools
   firebase init
   ```

2. Create a Firebase project

   ```
   firebase project:create
   ```

3. Setup the Firebase project for FSTQ

   ```sh
   ./scripts/setup_firebase.sh
   ```

## 2. Add items to the queue from a javascript client app

- Install the [javascript client lib](#)

  ```sh
  npm install fstq-client
  ```

- Load and initialize the client lib

  ```js
  import fstq from fstq
  fstq.init(FIREBASE_CONFIG)
  ```

- Add some items to the queue
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

## 3. Process the items with local or remote python workers

- Install the [python admin/worker lib and CLI](#)

  ```sh
  pip install fstq
  ```

- Write a simple worker demo

  ```python
  import fstq
  import model

  @fstq.run
  def process(items):
      results = [model(item['text']) for item in items]
      return [{'text': t} for t in results]
  ```

- Generate a `firebase_credentials` json for your worker in
  [the firebase console](#)

- Start a local worker:

  - Make sure you've installed and setup [Docker](#).

  - Start the example worker using Docker
    ```sh
    cd example/worker
    export GOOGLE_APPLICATION_CREDENTIALS='/path/to/worker/credentials.json'
    docker build . -t fstq-demo
    docker run -rm \
      -v $GOOGLE_APPLICATION_CREDENTIALS:'/credentials.json' \
      -e GOOGLE_APPLICATION_CREDENTIALS='/credentials.json' \
      fstq-demo -- \
          --queue 'fstq-demo' \
          --max_batch_size 5
    ```

- Start an autoscaling remote cluster of GPU workers using GKE:

  - Make sure you've installed and setup [gcloud](#).

  - Deploy the worker's image and attach a gpu node pool to the queue

    ```sh
    ./scripts/deploy_gke.sh . \
        --queue 'my-queue' \
        --max_batch_size 5 \
        --gpu nvidia-t4 \
        --min_workers 0 \
        --max_workers 5 \
        --credentials '/path/to/worker/credentials.json'
    ```

## 4. Monitor

- Track your key queue metrics with the `fstq monitor` command:

  ```sh
  fstq monitor 'my-queue'
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
  | Filling rate:                3 items/s       |
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
