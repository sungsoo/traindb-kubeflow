from kubeflow.metadata import metadata

# Kubeflow Metadata 객체 생성
metadata_client = metadata.Metadata()

# kubeflow-uuid를 사용하여 Pod ID 생성
pod_id = metadata_client.generate_uuid()