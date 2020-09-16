# FSTQ

A fast and easy to use task queue for intensive workloads (ML, GPU, video render...etc)

- **Transparently mix workers environments:** You can plug-in workers at any time
  and from anywhere to help process the queue: For instance you could start with your
  home computer, add your work's computer at night or even use some GPUs from Colab.
- **Only processed once:** Guarantee that each item will only be processed once,
  even if multiple workers are listening to the queue at the same time.
- **Dynamic batching:** Automatically and dynamically bulk queued items by
  batches to accelerate processing.
<!-- - **Managed Autoscaling Workers:** automatically scale-up remote GPU nodes
  if needed during traffic bursts -->

# Overview

### 1. Add items to process from a javascript client app

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
  }
  for (let i = 0; i < 1000; i++) {
    process()
  }
  ```

### 2. Process the items with python workers

- Install the [python admin/worker lib and CLI](#)

  ```sh
  pip install fstq
  ```

- Initialize fstq

  ```sh
  fstq init
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

- Start the worker locally

  ```sh
  fstq run . \
    --queue 'fstq-demo' \
    --max_batch_size 5
  ```

<!-- - Add a remote autoscaling GPU cluster to help during bursts
  ```sh
  fstq deploy . \
    --queue 'fstq-demo' \
    --max_batch_size 5 \
    --min_workers 0 \
    --max_workers 5 \
    --gpu nvidia-t4 \
    --autoscaling economical
  ``` -->

# Get Started

- [Getting Started](docs/getting-started.md)
