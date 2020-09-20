from google import api_core
from google.cloud.container_v1.services import cluster_manager
from google.cloud.container_v1.types import CreateNodePoolRequest
from google.cloud.container_v1.types import DeleteNodePoolRequest
from google.cloud.container_v1.types import GetNodePoolRequest
from google.cloud.container_v1.types import GetOperationRequest
from google.cloud.container_v1.types import GetServerConfigRequest
from google.cloud.container_v1.types import NodeConfig
from google.cloud.container_v1.types import NodePool
from google.cloud.container_v1.types import AcceleratorConfig
import subprocess
import time

from fstq.types import Autoscaler, Collections, Defaults, Metrics

client = cluster_manager.ClusterManagerClient()


def _wait_complete(operation, project: str, wait_seconds: int = 1):
    """Blocks until an operation completes."""
    zone = Defaults.ZONE
    op_name = f'projects/{project}/locations/{zone}/operations/{operation.name}'
    while True:
        time.sleep(wait_seconds)
        op = client.get_operation(GetOperationRequest(name=op_name))
        if op.end_time:
            return True


def generate_kubeconfig(project: str):
    zone = Defaults.ZONE
    cluster = Defaults.CLUSTER_ID
    process = subprocess.Popen([
        'gcloud', 'container', 'clusters', 'get-credentials', cluster,
        '--zone', zone, '--project', project
    ])
    for line in process.communicate():
        if line is None:
            continue
        output, error = line
        if error:
            print(error)
        if output:
            print(output)


def node_pool_exists(queue: str, project: str):
    zone = Defaults.ZONE
    cluster = Defaults.CLUSTER_ID
    name = f'projects/{project}/locations/{zone}/clusters/{cluster}/nodePools/{queue}'
    try:
        pool = client.get_node_pool(GetNodePoolRequest(name=name))
        if pool:
            return True
    except api_core.exceptions.NotFound:
        pass
    return False


def create_node_pool(queue: str, project: str, gpu: str, machine: str,
                     preemptible: bool):
    zone = Defaults.ZONE
    cluster = Defaults.CLUSTER_ID
    # TODO: Ensure that the project has an 'fstq' GKE cluster
    # TODO: Ensure project quotas allow the appropriate resources

    # Create a node pool with queue name and selected GPU
    # https://googleapis.dev/python/container/latest/container_v1/services.html
    accelerators = []
    if gpu:
        accelerators = [
            AcceleratorConfig(accelerator_type=gpu, accelerator_count=1)
        ]
    oauth_scopes = [
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/devstorage.read_only',
    ]
    node_config = NodeConfig(machine_type=machine,
                             preemptible=preemptible,
                             accelerators=accelerators,
                             oauth_scopes=oauth_scopes)
    node_pool = NodePool(name=queue, config=node_config, initial_node_count=1)
    node_pool_request = CreateNodePoolRequest(project_id=project,
                                              zone=zone,
                                              cluster_id=cluster,
                                              node_pool=node_pool)
    # Initialize the GKE client.
    op = client.create_node_pool(node_pool_request)
    # Wait until the operation has completed.
    _wait_complete(op, project)


def delete_node_pool(queue: str, project: str):
    zone = Defaults.ZONE
    cluster = Defaults.CLUSTER_ID
    name = f'projects/{project}/locations/{zone}/clusters/{cluster}/nodePools/{queue}'
    try:
        op = client.delete_node_pool(DeleteNodePoolRequest(name=name))
        # Wait until the operation has completed.
        _wait_complete(op, project)
    except api_core.exceptions.NotFound:
        print(f'Node pool "{name}" not found.')