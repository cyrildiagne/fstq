import click
import firebase_admin
import firebase_admin.firestore
import os
import sys
from . import docker, metrics
from fstq.common import Collections, Metrics

firebase_admin.initialize_app()


@click.command()
@click.argument("queue")
@click.option("--project", required=True, help="The Firebase project id.")
def create(queue: str, project: str):
    """Create a new queue."""
    #TODO: Make sure Firestore is enabled in project

    # Get queue doc ref.
    db = firebase_admin.firestore.client()
    queue_col = db.collection(Collections.ROOT).document(queue)
    # Initialize metrics.
    metrics_doc = queue_col.collection(
        Collections.METADATA.value).document('metrics')
    # Make sure queue doesn't exists already.
    if metrics_doc.get().exists:
        raise Exception('Error: Queue already exists')
    metrics_doc.set({
        Metrics.NUM_QUEUED: 0,
        Metrics.NUM_PROCESSED: 0,
        Metrics.NUM_FAILED: 0,
    })

    #TODO: Deploy the Functions

    print(f'Queue "{queue}" created.')


@click.command()
@click.option("--queue", required=True, help="The FSTQ queue.")
@click.option("--project", required=True, help="The Firebase project id.")
def delete():
    """Delete a queue."""
    #TODO: Delete the queue
    print('WIP')


@click.command()
@click.option("--queue", required=True, help="The FSTQ queue.")
@click.option("--credentials", required=True, help="Path to the credentials.")
@click.option("--max_batch_size", default=1, help="Max batch size.")
def process(queue: str, credentials: str, max_batch_size: int):
    """Process the queue locally using Docker."""
    # Build the docker image.
    tag = f'{queue}:latest'
    docker.build(tag)
    # Run the Docker image.
    volumes = [f'{credentials}:/credentials.json']
    env = {'GOOGLE_APPLICATION_CREDENTIALS': '/credentials.json'}
    cmd = ['python', 'main.py']
    args = ['--queue', queue, '--max_batch_size', str(max_batch_size)]
    docker.run(tag, volumes, env, cmd + args)


@click.command()
@click.option("--queue", required=True, help="The FSTQ queue.")
@click.option("--project", required=True, help="The Firebase project id.")
def deploy(queue: str, project: str):
    """Deploy a worker to GKE."""
    #TODO: Ensure that gcloud is installed and configured
    #TODO: Ensure that the project has an 'fstq' GKE cluster
    #TODO: Ensure that the cluster has a fstq node pool with the selected GPU
    #TODO: Set a Kubernetes secret with the Firebase credentials provided
    #TODO: Build a Docker image from the cwd and push it to GCR
    #TODO: Create/update a deployment using the image built and the secret

    #TODO: Deploy the gkeAutoscaler fn with a firestore trigger on the queue

    print('WIP')


@click.command()
@click.option("--project", required=True, help="The Firebase project id.")
def end():
    """End a worker pool."""
    #TODO: Delete the deployment
    #TODO: Scale down node pool to 0
    #TODO: Delete the gkeAutoscaler fn
    print('WIP')


@click.command()
@click.argument("queue")
def monitor(queue: str):
    """Print queue metrics."""
    db = firebase_admin.firestore.client()
    metrics.snapshot(db, queue)


@click.group()
def main():
    pass


main.add_command(create)
main.add_command(process)
main.add_command(deploy)
main.add_command(monitor)