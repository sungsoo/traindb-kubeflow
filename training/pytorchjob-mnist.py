from kubernetes.client import V1PodTemplateSpec
from kubernetes.client import V1ObjectMeta
from kubernetes.client import V1PodSpec
from kubernetes.client import V1Container

from kubeflow.training import V1ReplicaSpec
from kubeflow.training import KubeflowOrgV1PyTorchJob
from kubeflow.training import KubeflowOrgV1PyTorchJobSpec
from kubeflow.training import V1RunPolicy
from kubeflow.training import TrainingClient

name = "pytorch-dist-mnist-gloo"
namespace = "traindb"
container_name = "pytorch"

container = V1Container(
    name=container_name,
    image="gcr.io/kubeflow-ci/pytorch-dist-mnist-test:v1.0",
    args=["--backend", "gloo"],
)

replica_spec = V1ReplicaSpec(
    replicas=1,
    restart_policy="OnFailure",
    template=V1PodTemplateSpec(
        metadata=V1ObjectMeta(
            name=name,
            namespace=namespace,
            annotations={
                "sidecar.istio.io/inject": "false"
            }
        ),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name=container_name,
                    image="gcr.io/kubeflow-ci/pytorch-dist-mnist-test:v1.0",
                    args=["--backend", "gloo"],
                )
            ]
        )
    )
)

pytorchjob = KubeflowOrgV1PyTorchJob(
    api_version="kubeflow.org/v1",
    kind="PyTorchJob",
    metadata=V1ObjectMeta(name=name, namespace=namespace),
    spec=KubeflowOrgV1PyTorchJobSpec(
        run_policy=V1RunPolicy(clean_pod_policy="None"),
        pytorch_replica_specs={
            "Master": replica_spec,
            "Worker": replica_spec
        },
    ),
)

training_client = TrainingClient()
training_client.delete_pytorchjob(name)
training_client.create_pytorchjob(pytorchjob, namespace=namespace)

training_client.get_pytorchjob(name).metadata.name

training_client.get_job_conditions(name=name, namespace=namespace, job_kind="PyTorchJob")

pytorchjob = training_client.wait_for_job_conditions(name=name, namespace=namespace, job_kind="PyTorchJob")

print(f"Succeeded number of replicas: {pytorchjob.status.replica_statuses['Master'].succeeded}")

training_client.is_job_succeeded(name=name, namespace=namespace, job_kind="PyTorchJob")

training_client.get_job_logs(name=name, namespace=namespace, container=container_name)

training_client.delete_pytorchjob(name)


