import click
import firebase_admin
import firebase_admin.firestore
import os
import sys

from . import docker, metrics, gke, kubectl
from fstq.types import Autoscaler, Collections, Defaults, Metrics

app = None


def _get_db(project):
    """Initialize the Firestore client."""
    global app
    if app is None:
        app = firebase_admin.initialize_app(None,
                                            options={'projectId': project})
    db = firebase_admin.firestore.client()
    return db


def _init_metrics(db, queue):
    # Get the queue doc ref.
    queue_col = db.collection(Collections.ROOT).document(queue)
    metrics_doc = queue_col.collection(
        Collections.METADATA).document('metrics')
    # Make sure the queue doesn't exist already.
    if metrics_doc.get().exists:
        print('Queue already exists')
        exit()
    # Set the initial metrics.
    metrics_doc.set({
        Metrics.NUM_QUEUED: 0,
        Metrics.NUM_PROCESSED: 0,
        Metrics.NUM_FAILED: 0,
    })


def _stop_worker_pool(queue, project):
    # Delete the deployment
    print(f'Deleting deployment "{queue}"...')
    kubectl.delete(queue)

    # Delete the node pool
    print(f'Deleting node pool "{queue}"...')
    gke.delete_node_pool(queue, project)
    print(f'Done.')

    # TODO: Delete the gkeAutoscaler fn


def _init_autoscaler_settings(db, queue, max_batch_size, min_workers,
                              max_workers):
    # Get the queue doc ref.
    queue_col = db.collection(Collections.ROOT).document(queue)
    # Set the autoscaler values.
    gke_doc = queue_col.collection(Collections.METADATA).document('gke')
    gke_doc.set({
        Autoscaler.MAX_BATCH_SIZE: max_batch_size,
        Autoscaler.MIN_WORKERS: min_workers,
        Autoscaler.MAX_WORKERS: max_workers,
    })


@click.command()
@click.argument("queue")
@click.option("--project", required=True, help="The Firebase project id.")
def create(queue: str, project: str):
    """Create a new queue."""
    # Initialize the Firestore client
    db = _get_db(project)
    _init_metrics(db, queue)
    print(f'Queue "{queue}" created.')


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
@click.argument('worker_root')
@click.option("--queue", required=True, help="The FSTQ queue.")
@click.option("--project", required=True, help="The Firebase project id.")
@click.option("--credentials",
              required=True,
              help="Path to the firebase credentials.")
@click.option("--max_batch_size", default=1, help="Max batch size.")
@click.option("--min_workers", default=0, help="Min number of workers.")
@click.option("--max_workers", default=8, help="Max number of workers.")
@click.option("--gpu", help="GPU.")
@click.option("--machine", default="n1-standard-2", help="The machine type.")
@click.option("--preemptible", default=False, help="Flag for preemptible.")
def deploy(worker_root: str, queue: str, project: str, credentials: str,
           max_batch_size: int, min_workers: int, max_workers: int, gpu: str,
           machine: str, preemptible: bool):
    """Deploy a worker to GKE."""
    print('** WIP **')

    # Check if a node pool already exists for that queue
    if gke.node_pool_exists(queue, project):
        print(f'Using existing {queue} node pool with the same configuration.')
    else:
        print(f'Creating node pool')
        gke.create_node_pool(queue,
                             project,
                             gpu=gpu,
                             machine=machine,
                             preemptible=preemptible)
        #TODO: Set a Kubernetes secret with the Firebase credentials provided
        print(f'Node pool created.')

    # Generate kubeconfig
    gke.generate_kubeconfig(project)

    tag = f'gcr.io/{project}/{queue}:latest'

    print(f'Building image')
    # Navigate to worker's root
    init_cwd = os.getcwd()
    os.chdir(worker_root)
    try:
        # Build the Docker image
        docker.build(tag)
    except Exception as e:
        print(e)
        os.chdir(init_cwd)
        exit()
    # Go back to initial dir
    os.chdir(init_cwd)
    print(f'Image built.')

    # Push the image to the GCR
    print(f'Pushing image to {tag}')
    docker.push(tag)

    # Push the credentials
    print('Pushing credentials as cluster secret')
    with open(credentials) as f:
        kubectl.push_credentials(f.read())

    # Apply the deployment using the image built
    print(f'Launching deployment')
    needs_gpu = gpu is not None
    kubectl.deploy(queue, tag, needs_gpu)

    # Configure autoscaler values
    print(f'Updating autoscaler metadata')
    db = _get_db(project)
    _init_autoscaler_settings(db,
                              queue,
                              max_batch_size=max_batch_size,
                              min_workers=min_workers,
                              max_workers=max_workers)

    # TODO: Deploy the gkeAutoscaler fn
    print(f'Done')


@click.command()
@click.option("--queue", required=True, help="The FSTQ queue.")
@click.option("--project", required=True, help="The Firebase project id.")
def stop(queue: str, project: str):
    """Stops a worker pool."""
    _stop_worker_pool(queue, project)


@click.command()
@click.argument("queue")
@click.option("--project", required=True, help="The Firebase project id.")
def monitor(queue: str, project: str):
    """Print queue metrics."""
    db = _get_db(project)
    metrics.snapshot(db, queue)


@click.group()
def main():
    if os.getenv('FIRESTORE_EMULATOR_HOST'):
        print('** USING THE FIRESTORE EMULATOR **')


# Queue management
main.add_command(create)

# Worker commands
main.add_command(process)
main.add_command(deploy)
main.add_command(stop)

# Monitor
main.add_command(monitor)