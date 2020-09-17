def init(project_id: str):
    """Initialize the firebase project."""
    #TODO: Make sure Firestore is enabled
    #TODO: Create the security rules
    #TODO: Deploy the Functions
    return

def run():
    """Run a worker locally using Docker."""
    #TODO: Ensure Docker is installed and running
    #TODO:
    # export GOOGLE_APPLICATION_CREDENTIALS='/path/to/worker/credentials.json'
    # docker build . -t fstq-demo
    # docker run -rm \
    #     -v $GOOGLE_APPLICATION_CREDENTIALS:'/credentials.json' \
    #     -e GOOGLE_APPLICATION_CREDENTIALS='/credentials.json' \
    #     fstq-demo -- \
    #         --queue 'fstq-demo' \
    #         --max_batch_size 5
    pass

def deploy():
    """Deploy a worker to GKE."""
    #TODO: Ensure gcloud is installed and configured
    #TODO: Ensure that the project has a  GKE cluster
    #TODO: Ensure that the cluster has a fstq node pool with the selected GPU
    #TODO: Set a Kubernetes secret with the Firebase credentials provided
    #TODO: Build a Docker image from the cwd and push it to GCR
    #TODO: Create/update a deployment using the image built and the secret
    #TODO: Start autoscaling the workers based on the queue's size / proc rate
    pass

def monitor():
    """Print queue metrics."""
    #TODO: print stats
    pass