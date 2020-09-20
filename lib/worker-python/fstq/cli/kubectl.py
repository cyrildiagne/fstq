from kubernetes import client, config
import base64


def push_credentials(credentials: str):
    config.load_kube_config()
    metadata = client.V1ObjectMeta(name='credentials')
    credentials_b64 = base64.b64encode(str.encode(credentials)).decode()
    secret = client.V1Secret(api_version="v1",
                             type='Opaque',
                             metadata=metadata,
                             data={'credentials.json': credentials_b64})
    v1 = client.CoreV1Api()
    try:
        v1.create_namespaced_secret(namespace="default", body=secret)
    except client.rest.ApiException as e:
        # TODO: handle 'AlreadyExist'
        if 'AlreadyExists' in e.body:
            print('Credentials already exist. Skipping')
        else:
            print(e)


def deploy(queue: str, tag: str, needs_gpu: bool):
    # Load kube config on deploy
    config.load_kube_config()
    v1 = client.AppsV1Api()
    # Handle GPU
    resources = None
    if needs_gpu:
        resources = client.V1ResourceRequirements(limits={
            "nvidia.com/gpu": "1",
        })
    # Configureate Pod template container
    env = client.V1EnvVar(name='GOOGLE_APPLICATION_CREDENTIALS',
                          value='/secrets/credentials.json')
    volumes_mounts = client.V1VolumeMount(name='secrets',
                                          mount_path='/secrets',
                                          read_only=True)
    container = client.V1Container(name=queue,
                                   image=tag,
                                   resources=resources,
                                   env=[env],
                                   volume_mounts=[volumes_mounts],
                                   command=['python', 'main.py'])
    volumes = client.V1Volume(
        name='secrets',
        secret=client.V1SecretVolumeSource(secret_name='credentials'))
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": queue}),
        spec=client.V1PodSpec(containers=[container], volumes=[volumes]))
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(replicas=1,
                                   template=template,
                                   selector={'matchLabels': {
                                       'app': queue
                                   }})
    # Instantiate the deployment object
    deployment = client.V1Deployment(api_version="apps/v1",
                                     kind="Deployment",
                                     metadata=client.V1ObjectMeta(name=queue),
                                     spec=spec)

    try:
        v1.create_namespaced_deployment(body=deployment, namespace="default")
    except client.rest.ApiException as e:
        # TODO: handle 'AlreadyExist'
        if 'AlreadyExists' in e.body:
            print('Deployment already exist. Skipping')
        else:
            print(e)


def delete(queue: str):
    # Load kube config on deploy
    config.load_kube_config()
    # Delete deployment
    v1 = client.AppsV1Api()
    try:
        v1.delete_namespaced_deployment(name=queue,
                                        namespace="default",
                                        body=client.V1DeleteOptions(
                                            propagation_policy='Foreground',
                                            grace_period_seconds=5))
    except client.rest.ApiException as e:
        if e.reason.lower() == 'not found':
            print('Deployment not found')
        else:
            print(e)