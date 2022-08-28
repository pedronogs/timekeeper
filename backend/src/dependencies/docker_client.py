import docker
import io
import tarfile


class AppDockerClient:

    master_container_uuid: str = "b11d984f2f2d77323eed943f9b0f7b02adc0495fc331006412c2ff3d0042d3d8"
    shared_volume_name: str = "timekeeper-agent-scripts"
    shared_volume_mount_path: str = "/opt/timekeeper"
    int_network_name: str = "timekeeper-int-network"
    int_network_id: str

    def __init__(self):
        self.docker_client = docker.from_env()

        # Create internal docker network between master and agents
        found_docker_networks = self.docker_client.networks.list(names=[self.int_network_name])
        if len(found_docker_networks) == 0:
            self.docker_client.networks.create(self.int_network_name)
        elif len(found_docker_networks) > 1:
            self.docker_client.networks.prune({"name": self.int_network_name})

        found_docker_networks = self.docker_client.networks.list(names=[self.int_network_name])
        self.int_network_id = found_docker_networks[0].id

        try:
            self.docker_client.volumes.get(self.shared_volume_name)
        except docker.errors.NotFound:
            self.docker_client.volumes.create(self.shared_volume_name)

        # Copy agent wrapper script to shared volume
        with open("./backend/wrapper.py", "rb") as f:
            wrapper_bytes = f.read()
        self.copy_file_to_shared_volume(wrapper_bytes, "wrapper.py")

    def __call__(self):
        return self.docker_client

    def get_int_network(self):
        return self.docker_client.networks.get(self.int_network_id)

    def get_shared_volume_name(self):
        return self.shared_volume_name

    def get_master_container(self):
        return self.docker_client.containers.get(self.master_container_uuid)

    # Copy file to shared volume between master and agent containers
    def copy_file_to_shared_volume(self, file_content: bytes, file_name: str):
        src_stream = io.BytesIO(file_content)
        dst_stream = io.BytesIO()
        with tarfile.open(fileobj=dst_stream, mode='w|') as tar:
            info = tarfile.TarInfo(name=file_name)
            info.size = src_stream.getbuffer().nbytes
            tar.addfile(info, src_stream)
        dst_stream.seek(0)

        master_container = self.get_master_container()
        master_container.put_archive(self.shared_volume_mount_path, dst_stream)
