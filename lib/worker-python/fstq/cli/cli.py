import click
import firebase_admin
import firebase_admin.firestore
import os
import sys

from . import docker, metrics


@click.command()
@click.argument("queue_name")
@click.option("--project", required=True, help="The Firebase project id.")
def create(queue_name: str, project: str):
    """Create a new queue."""
    #TODO: Make sure Firestore is enabled
    #TODO: Create the security rules
    #TODO: Deploy the Functions
    #TODO: Create empty doc
    print('WIP')


@click.command()
@click.option("--queue", required=True, help="The FSTQ queue.")
@click.option("--credentials", required=True, help="Path to the credentials.")
@click.option("--max_batch_size", default=1, help="Max batch size.")
def process(queue: str, credentials: str, max_batch_size: int):
    """Process the queue locally using Docker."""
    print('Building the Docker image...')
    tag = f'{queue}:latest'
    docker.build(tag)
    print('Running the Docker image...')
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
def delete():
    """Delete a GKE worker pool."""
    #TODO: Delete the deployment
    #TODO: Delete the gkeAutoscaler fn
    #TODO: Scale down node pool to 0
    print('WIP')


@click.command()
@click.argument("queue")
def monitor(queue: str):
    """Print queue metrics."""
    db = _get_db()
    metrics.snapshot(db, queue)


@click.group()
def main():
    pass


def _get_db():
    firebase_admin.initialize_app()
    db = firebase_admin.firestore.client()
    return db


main.add_command(create)
main.add_command(process)
main.add_command(deploy)
main.add_command(monitor)