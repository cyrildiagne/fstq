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

- Start a local worker

  ```sh
  export GOOGLE_APPLICATION_CREDENTIALS='/path/to/worker/credentials.json'
  ```

  ```sh
  fstq run . \
    --queue 'fstq-demo' \
    --max_batch_size 5
  ```

- Start an autoscaling remote cluster of GPU workers

  ```sh
  WIP
  ```
