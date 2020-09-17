import click
import os
import sys

import firebase_admin
import firebase_admin.firestore


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
def run(queue: str, credentials: str, max_batch_size: int):
    """Run a worker locally using Docker."""
    import docker
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        exit('Error connecting to Docker. Is it running?')

    if not os.path.exists('./Dockerfile'):
        exit('Could not find Dockerfile in current context.')

    tag = f'{queue}:latest'

    # Build Docker image.
    resp = client.api.build(path='.', rm=True, tag=tag, decode=True)
    build_success = None
    for line in resp:
        event = list(line.keys())[0]
        if event in ('stream', 'error'):
            value = list(line.values())[0].strip()
            if value:
                print(value)
            if event == 'stream' and 'successfully tagged' in value.lower():
                build_success = True
        else:
            print(line)
    if not build_success:
        exit('Error building Docker image')

    # Run Docker image.
    print('Running docker image')
    cmd = [
        'python', 'main.py', '--queue', queue, '--max_batch_size',
        str(max_batch_size)
    ]
    container = client.containers.run(
        tag,
        command=cmd,
        volumes=[f'{credentials}:/credentials.json'],
        environment={'GOOGLE_APPLICATION_CREDENTIALS': '/credentials.json'},
        remove=True,
        stderr=True,
        detach=True)
    process = container.logs(stream=True)
    for line in process:
        sys.stdout.write(line.decode())


@click.command()
@click.option("--project", required=True, help="The Firebase project id.")
def deploy():
    """Deploy a worker to GKE."""
    #TODO: Ensure gcloud is installed and configured
    #TODO: Ensure that the project has a  GKE cluster
    #TODO: Ensure that the cluster has a fstq node pool with the selected GPU
    #TODO: Set a Kubernetes secret with the Firebase credentials provided
    #TODO: Build a Docker image from the cwd and push it to GCR
    #TODO: Create/update a deployment using the image built and the secret
    #TODO: Start autoscaling the workers based on the queue's size / proc rate
    print('WIP')


@click.command()
def monitor():
    """Print queue metrics."""
    #TODO: print stats
    print('WIP')


@click.group()
def main():
    pass


def _get_db():
    # Initialize firebase admin.
    firebase_admin.initialize_app()
    # Initialize firestore client.
    db = firebase_admin.firestore.client()
    return db


main.add_command(create)
main.add_command(run)
main.add_command(deploy)
main.add_command(monitor)