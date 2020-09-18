import docker
import os
import sys


def get_client():
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        exit('Error connecting to Docker. Is it running?')
    return client


def build(tag):
    """Build a Docker image."""
    if not os.path.exists('./Dockerfile'):
        exit('Could not find Dockerfile in current context.')

    # Build Docker image.
    client = get_client()
    resp = client.api.build(path='.', rm=True, tag=tag, decode=True)

    # Stream logs.
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


def run(tag, volumes, env, cmd):
    """Run a Docker container."""
    client = get_client()
    container = client.containers.run(tag,
                                      command=cmd,
                                      volumes=volumes,
                                      environment=env,
                                      remove=True,
                                      stderr=True,
                                      detach=True)
    process = container.logs(stream=True)
    for line in process:
        sys.stdout.write(line.decode())
