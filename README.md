# FSTQ

A simple task queue template for Firebase.

- **Ideal for intensive GPU inference**
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
- **Priority management**
  You can allocate a different priority to each item to control what gets handled first.
- **Always processed once**
  FSTQ guarantees that each item will only be processed
  once even if multiple workers are listening to the queue at the same time.


**Status:** Experimental 🧪

## 1. Setting up FSTQ

1. Create a [Firebase](http://firebase.google.com) project if you don't already have one
2. Install the FSTQ cli and lib
  
   ```sh
   git clone https://github.com/cyrildiagne/fstq
   pip install fstq/lib/worker-python
   ```

3. Initialize the project

   ```sh
   fstq init 'your-firebase-project-id'
   ```


<!--
2. Log in to your Google account:

   ```sh
   gcloud auth application-default login
   ```

3. Install and initialize the [Firebase tools](#)

   ```sh
   npm install -g firebase-tools && firebase init
   ```

4. Clone this template

   ```sh
   git clone https://github.com/cyrildiagne/fstq
   cd fstq
   ```

5. Install the CLI and python lib

   ```sh
   pip install lib/worker-python
   ```

6. Deploy the functions and firestore configuration

   ```sh
   firebase deploy --only firestore
   firebase deploy --only functions:push
   ```
-->

## 1. Create a queue

- Simply run
  ```sh
  fstq create 'fstq-demo'
  ```

## 2. Push items to the queue

- Items can be pushed to the queue using the [javascript client lib](lib/client-js).

  The [client example](example/client/src/index.js) shows how to add items
  to the queue and wait for the results:

  ```js
  import fstq from 'fstq'
  import config from './firebase-config.js'

  fstq.init(config)

  async function process() {
    const item = { text: 'hello world' }
    const task = await fstq.push('fstq-demo', item)
    const result = await task.result()
    console.log(result)
  }
  for (let i = 0; i < 10; i++) {
    process()
  }
  ```

  <details><summary><b>Instructions to run the client example</b></summary>
  <p>

  - Create a file `example/client/src/firebase-config.js` that exports your
    [firebase's web config]() such as:

    ```js
    export default {
      apiKey: 'XXXX',
      authDomain: 'xxx',
      ...
    }
    ```

  - Run
    ```sh
    cd example/client
    yarn install
    yarn run dev
    ```
  - Navigate to [http://localhost:8080](http://localhost:8080)
  - The items will be added to the queue and the results will be printed in the
    console as soon as they're available.

  </p></details>

## 3. Process the queue

- Items in the queue can be processed using the [python worker lib](sdl/worker-python).

  The [worker example](example/worker/main.py) shows how to process incoming items:

  ```python
  import fstq

  def reverse(text):
      return text[::-1]

  @fstq.process
  def process(batch):
      results = [reverse(item['text']) for item in batch]
      return [{'text': t} for t in results]
  ```

  <details><summary><b>Instructions to run the worker example</b></summary>
  <p>

  - First, generate a credentials json file for your worker in [the firebase console](#)
  - Then you can run the worker:

    <details><summary>Locally with python</summary>
    <p>

    - Install the requirements (preferably in a [virtualenv]()).

      ```sh
      virtualenv venv
      source venv/bin/activate
      pip install -r example/worker/requirements.txt
      ```

    - Set the `GOOGLE_APPLICATION_CREDENTIALS` env:

      ```sh
      export GOOGLE_APPLICATION_CREDENTIALS='/path/to/credentials.json'
      ```

    - Start the example worker

      ```sh
      python example/worker/main.py \
          --queue 'fstq-demo' \
          --max_batch_size 5
      ```

    </p></details>

    <details><summary>Locally as Docker container</summary>
    <p>

    - Make sure you've installed and setup [Docker](#).

    - Start the example worker using Docker

      ```sh
      cd example/worker
      fstq process . \
          --queue 'fstq-demo' \
          --credentials '/path/to/worker/credentials.json' \
          --max_batch_size 5
      ```

    </p></details>

    <details><summary>From a Jupyter notebook / Colab</summary>
    <p>

    - If you're using Colab, upload your credentials json and setup the credentials env:

      ```sh
      %env GOOGLE_APPLICATION_CREDENTIALS='/path/to/credentials.json'
      ```
      
    - Setup the queue env in the notebook:

      ```sh
      %env FSTQ_PROJECT_ID='your-project-id'
      %env FSTQ_QUEUE='fstq-demo'
      %env FSTQ_MAX_BATCH_SIZE=5
      ```

    - Simply run the cell that contains the `@fstq.process` decorated function
      and it will start pulling and processing items.

    </p></details>

    <details><summary>Remotely in a GKE cluster</summary>
    <p>

    - Make sure you've installed and setup [gcloud](#).

    - Make sure docker is configured to be able to push to gcr:

      ```sh
      gcloud auth configure-docker
      ```

    - Deploy the worker's image and attach a gpu node pool to the queue

      ```sh
      fstq deploy ./example/worker \
          --queue 'fstq-demo' \
          --credentials '/path/to/worker/credentials.json' \
          --max_batch_size 5 \
          --gpu nvidia-tesla-t4 \
          --min_workers 0 \
          --max_workers 5
      ```

    - Deploy the gkeAutoscaler function:

      ```sh
      firebase deploy --only functions:gkeAutoscaler
      ```

      </p></details>

    </p></details>

## 4. Monitor

- Track some key metrics with the `fstq monitor` command:

  ```sh
  fstq monitor 'fstq-demo'
  ```

  Output (WIP):

  ```
  ┌──────────────────────────────────────────────────┐
  │ fstq-demo (my-firebase-project)                  │
  ├──────────────────────────────────────────────────┤
  │ Queued:                      52 items            │
  │ Processed:                   3045 items          │
  │ Failed:                      20 items            │
  ├──────────────────────────────────────────────────┤
  │ Incoming rate:               3 items/s           │
  │ Processing rate:             2 items/s           │
  │ Avg latency:                 2400 ms             │
  ├──────────────────────────────────────────────────┤
  │ Local Workers:               1                   │
  │ GKE Workers:                 3 (target: 8)       │
  └──────────────────────────────────────────────────┘
  ```

  <!--
    ```sh
    fstq monitor 'fstq-demo' --workers
    ```

    ```

     Local Workers                         Total: 1
    ┌──────────────────────────────────────────────┐
    │ Home laptop                                  │
    ├──────────────────────────────────────────────┤
    │ Status:                      PROCESSING      │
    │ Up time:                     22d 6h 32min    │
    │ Avg time per item:           3456 ms         │
    │ CPU:                         63% (2 CPU)     │
    │ Mem:                         72% (8.0 Gb)    │
    └──────────────────────────────────────────────┘

     GKE Workers                      Total: 3 / 16
    ┌──────────────────────────────────────────────┐
    │ Nvidia-T4                                    │
    ├──────────────────────────────────────────────┤
    │ Status:                      PROCESSING      │
    │ Up time:                     2h 18min        │
    │ Avg time per item:           2156 ms         │
    │ CPU:                         63% (2 vCPU)    │
    │ Mem:                         72% (8.0 Gib)   │
    │ GPU:                         12% (5840 cc)   │
    │ GPU Mem:                     24% (16.0 Gib)  │
    ├──────────────────────────────────────────────┤
    │ Nvidia-T4                                    │
    ├──────────────────────────────────────────────┤
    │ Status:                      PROCESSING      │
    │ Up time:                     18min           │
    │ Avg time per item:           1956 ms         │
    │ CPU:                         63% (2 vCPU)    │
    │ Mem:                         72% (8.0 Gib)   │
    │ GPU:                         12% (5840 cc)   │
    │ GPU Mem:                     22% (16.0 Gib)  │
    ├──────────────────────────────────────────────┤
    │ Nvidia-T4                                    │
    ├──────────────────────────────────────────────┤
    │ Status:                      STARTING        │
    │ Up time:                     18min           │
    └──────────────────────────────────────────────┘
    ``` -->
