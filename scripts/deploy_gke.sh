# TODO:
# - Ensure that the project has a  GKE cluster (or create one)
# - Ensure that the cluster has an autoscaling node pool with the selected GPU (or create one)
# - Set a Kubernetes secret with the Firebase credentials provided
# - Build a Docker image from the cwd and push it to GCR
# - Create/update a deployment using the image built and the credentials secret
# - Start autoscaling the workers based on the queue's size / processing rate
