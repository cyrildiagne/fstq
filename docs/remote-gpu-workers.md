# Autoscaling Remote GPU Workers

## Using GKE

Make sure you've installed and setup [gcloud](#).

- Generate a `firebase_credentials` json for your worker in
  [the firebase console](#)
- Deploy the worker's image and attach a gpu node pool to the queue

  ```sh
  fstq deploy_gke . \
      --queue 'my-queue' \
      --max_batch_size 5 \
      --gpu nvidia-t4 \
      --min_workers 0 \
      --max_workers 5 \
      --firebase_credentials '/path/to/worker/credentials.json'
  ```

  This command will:

  - Ensure that the project has a [GKE](#) cluster (or create one)
  - Ensure that the cluster has an autoscaling node pool with the selected GPU (or create one)
  - Set a [Kubernetes secret](#) with the Firebase credentials provided
  - Build a Docker image from the cwd and push it to [GCR](#)
  - Create/update a deployment using the image built and the credentials secret
  - Start autoscaling the workers based on the queue's size / processing rate

<!-- - `autoscaling economical` is a generic autoscaling strategy that will instruct
  the cluster to scale conservatively in order to minimize costs.
  For more information: [Remote GPUs autoscaling](#) -->

## Monitor

You can track your queue's remote GPUs with the `fstq monitor` command:

```sh
fstq monitor 'my-queue'

"""

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
"""
```
