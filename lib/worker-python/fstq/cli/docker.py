import docker
import os
import sys


def build_and_run(tag, volumes, env, cmd):
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        exit('Error connecting to Docker. Is it running?')

    if not os.path.exists('./Dockerfile'):
        exit('Could not find Dockerfile in current context.')

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
    print('Running docker image...')
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