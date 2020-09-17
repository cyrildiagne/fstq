# FSTQ

A fast and simple task queue for intensive workloads (ML, GPU, video
rendering...etc) using Firebase.

<!-- - **Ideal for intensive GPU inference**

  FSTQ's queue / worker architecture is
  ideal for long running GPU processes (> 1s) since concurrency is hard to
  manage on GPU via HTTP and autoscaling production GPUs is often slow.

- **Never timeout**

  Your service will have no problem handling surges of
  thousands of QPS (which would be very difficult to handle on GPU via HTTP).
  FSTQ makes sure all payloads are stored until a worker becomes available, and
  serves the results back as soon as they're ready.

- **Add new workers at anytime, from anywhere**

  You can quickly connect new
  workers from any environment to help process the queue: For instance you
  could start processing the queue with your home computer, then add your work's
  computer at night and even use some GPUs from Colab during traffic bursts.

- **Autoscale remote GPU Workers**

  You can also easily add a cluster of remote
  GPUs that will automatically scale with the rate of items being added/processed.

- **Dynamic batching**

  Items are automatically and dynamically bulked in
  batches to dramatically speep up GPU inference.

- **Always processed once**

  FSTQ guarantees that each item will only be processed
  once even if multiple workers are listening to the queue at the same time. -->

## 1. Setting up

1. Create a [Firebase]() project
2. Install and initialize the [Firebase tools](#)

   ```
   npm install -g firebase-tools
   firebase init
   ```

3. Install the fstq CLI

   ```sh
   pip install fstq
   ```

4. Initialize the Firebase project for FSTQ

   ```sh
   fstq init <firebase-project-id>
   ```

## 2. Add items to a processing queue

- Items can be added to a processing queue using the [javascript client lib](lib/client-js).

  The example client [example/client/src/index.js]() shows how to add items
  to a new `fstq-demo` queue (the queue is created when the first item added):

  ```js
  import fstq from 'fstq'
  import config from './firebase-config.js'

  fstq.init(config)

  async function process() {
    const task = await fstq.push('fstq-demo', { text: 'hello world' })
    const result = await task.result()
    console.log(result)
  }
  for (let i = 0; i < 10; i++) {
    process()
  }
  ```

  To run the example client:

  - `cd example/client`
  - Create a file `src/firebase-config.js` that exports your [firebase's web config]().
  - Run `yarn install`
  - Run `yarn run dev`
  - Navigate to [http://localhost:8080](http://localhost:8080)
  - It will add the items to the queue, and wait until the items are
    processed to print the result.

## 3. Process the items with python workers

- Items can be pulled from the queue and processed using the [python worker lib](sdl/worker-python).

  The example worker [example/worker/main.py]() shows how to process incoming items:

  ```python
  import fstq

  def reverse(text):
      return text[::-1]

  @fstq.run
  def process(batch):
      results = [reverse(item['text']) for item in batch]
      return [{'text': t} for t in results]
  ```

  To run the example worker:

  - First, generate a credentials json file for your worker in [the firebase console](#)
  - Then you can run the code (either or both):

    <details><summary>Locally with python</summary>
    <p>

    - Make sure you've installed the requirements (preferably in a virtualenv).

    - Start the example worker

      ```sh
      python example/worker/main.py \
          --queue 'fstq-demo' \
          --max_batch_size 5
      ```

    </p>

    <details><summary>Locally as Docker container</summary>
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

    <details><summary>Remotely in a cluster of GPU</summary>
    <p>

    - Make sure you've installed and setup [gcloud](#).

    - Deploy the worker's image and attach a gpu node pool to the queue

      ```sh
      fstq deploy ./example/worker \
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

  Local Workers:                        Total: 1
  +----------------------------------------------+
  | Home laptop                                  |
  |                                              |
  | Up time:                     22d 6h 32min    |
  | Status:                      PROCESSING      |
  | Avg time per item:           3456 ms         |
  | GPU Memory:                  24% (16.0 Gib)  |
  |----------------------------------------------|

  Remote Workers:                    Total: 2/16
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
