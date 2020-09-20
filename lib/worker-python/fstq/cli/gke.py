from google import api_core
from google.cloud.container_v1.services import cluster_manager
from google.cloud.container_v1.types import CreateNodePoolRequest
from google.cloud.container_v1.types import DeleteNodePoolRequest
from google.cloud.container_v1.types import GetNodePoolRequest
from google.cloud.container_v1.types import NodeConfig
from google.cloud.container_v1.types import NodePool
from google.cloud.container_v1.types import AcceleratorConfig

from fstq.types import Autoscaler, Collections, Defaults, Metrics

client = cluster_manager.ClusterManagerClient()


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
    node_config = NodeConfig(machine_type=machine,
                             preemptible=preemptible,
                             accelerators=accelerators)
    node_pool = NodePool(name=queue, config=node_config, initial_node_count=1)
    node_pool_request = CreateNodePoolRequest(project_id=project,
                                              zone=zone,
                                              cluster_id=cluster,
                                              node_pool=node_pool)
    # Initialize the GKE client.
    op = client.create_node_pool(node_pool_request)
    # TODO: wait until the operation has completed.
    print('WARNING: The GKE operation is running in the background')
    print('Please wait a few minutes for it to complete')
    print(op)


def delete_node_pool(queue: str, project: str):
    zone = Defaults.ZONE
    cluster = Defaults.CLUSTER_ID
    name = f'projects/{project}/locations/{zone}/clusters/{cluster}/nodePools/{queue}'
    try:
        op = client.delete_node_pool(DeleteNodePoolRequest(name=name))
        # TODO: wait until the operation has completed.
        print('WARNING: The GKE operation is running in the background')
        print('Please wait a few minutes for it to complete')
        print(op)
    except api_core.exceptions.NotFound:
        print(f'Node pool "{name}" not found.')