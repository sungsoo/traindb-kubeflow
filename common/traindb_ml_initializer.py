# Copyright 2023 The TrainDB-ML Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from unicodedata import name
from venv import create
import yaml
from os import path
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException

LOG = logging.getLogger(__name__)
TRAINDB_ML_SUCCESS = 1
TRAINDB_ML_FAILURE = 0

### Input parameters
CONF_PATH = '/opt/traindb/traindb-ml/conf/' # This is client side directory (Kubernetes/Kubeflow Python Client)
HOST_PATH = '/opt/traindb/traindb-ml/models' # This is host side directory
NAMESPACE = 'learned-model'
SYSTEM_NAME = 'traindb'
TDB_NAME = 'traindb-ml'

### Constants for template yaml files
PV_TEMPLATE = 'template-pv.yaml'
PVC_TEMPLATE = 'template-pvc.yaml'
VOL_POSTFIX = '-volume'
CLAIM_POSTFIX = '-claim'
PV_POSTFIX = '-pv.yaml'
PVC_POSTFIX = '-pvc.yaml'


class TrainDBMLInitializer():
    def __init__(self, tdbnamespace=None) -> None:
        self.namespace = tdbnamespace

    def open_yaml(self, filename):
        with open(filename) as f:  # 파일을 열어서
            pv_config = yaml.load(f, Loader=yaml.FullLoader)  # yaml 형식으로 불러온 후 pv_config 변수에 저장
        return pv_config  # pv_config 변수 반환

    def write_pv_yaml(self, filename, pv_config, name=TDB_NAME, system=SYSTEM_NAME, hostpath=HOST_PATH):
        # PV 설정에 이름과 라벨 추가
        pv_config['metadata'].update({'name': name + VOL_POSTFIX, 'labels': {'system': system, 'name': name + VOL_POSTFIX}})
        # PV 설정에 호스트 경로 추가
        pv_config['spec']['hostPath']['path'] = hostpath

        with open(filename, 'w') as f:
            yaml.dump(pv_config, f)

    def write_pvc_yaml(self, filename, pv_config, name=TDB_NAME, system=SYSTEM_NAME, hostpath=HOST_PATH):
        # PVC 설정에 이름과 네임스페이스 추가
        pv_config['metadata'].update({'name': name + CLAIM_POSTFIX, 'namespace': name})
        # PVC 설정에 selector 추가
        pv_config['spec']['selector']['matchLabels'].update({'system': system, 'name': name + VOL_POSTFIX})

        with open(filename, 'w') as f:
            yaml.dump(pv_config, f)

    ### Create YAML files
    def create_pv_yaml_from_template(self, conf_path, namespace, system=SYSTEM_NAME, hostpath=HOST_PATH):
        # PV 템플릿 파일 열기
        pv_conf = self.open_yaml(conf_path + PV_TEMPLATE)
        # PV YAML 파일 생성
        self.write_pv_yaml(conf_path + namespace + PV_POSTFIX, pv_conf, namespace, system, hostpath)

    def create_pvc_yaml_from_template(self, conf_path, namespace, system=TDB_NAME, hostpath=HOST_PATH):
        # PVC 템플릿 파일 열기
        pv_conf = self.open_yaml(os.path.join(conf_path, PVC_TEMPLATE))
        # PVC YAML 파일 생성
        yaml_filename = os.path.join(conf_path, namespace + PVC_POSTFIX)
        self.write_pvc_yaml(yaml_filename, pv_conf, namespace, system, hostpath)

    ### Deploy PV, PVC using YAML files
    def deploy_yaml(self, yaml_file, namespace=HOST_PATH):
        # Kubernetes API 설정
        config.load_kube_config()
        k8s_client = client.ApiClient()
        # YAML 파일로부터 PV, PVC 생성
        return utils.create_from_yaml(k8s_client, yaml_file, verbose=True)

    def get_pv_filename(self, conf_path, namespace):
        # PV YAML 파일 경로 반환
        return conf_path + namespace + PV_POSTFIX
    def get_pvc_filename(self, conf_path, namespace):
        # PVC YAML 파일 경로 반환
        return conf_path + namespace + PVC_POSTFIX

    def create_namespace(self, namespace=None):
        config.load_kube_config()
        if not namespace:
            print("namespace is not defined.")
            return TRAINDB_ML_FAILURE
        v1 = client.CoreV1Api()
        try:
            v1.read_namespace(name=namespace)
        except ApiException:
            body = client.V1Namespace(
                kind="Namespace",
                api_version="v1", 
                metadata=client.V1ObjectMeta(name=namespace)
            )
            try:
                v1.create_namespace(body=body)
            except ApiException as e:
                LOG.error("Exception when calling CoreV1Api->read_namespace: %s", e)
                return e
        return TRAINDB_ML_SUCCESS

    def delete_namespace(self, namespace=None):
        # 네임스페이스 삭제
        config.load_kube_config()
        v1 = client.CoreV1Api()
        try:
            v1.read_namespace(name=namespace)
        except ApiException as e:
            LOG.error(
                "Requested {namespace} does not exist. %s",
                e,
            )

        v1.delete_namespace(namespace)


    def init(self, tdb_namespace=NAMESPACE):
        # PV, PVC YAML 파일 생성
        self.create_pv_yaml_from_template(CONF_PATH, tdb_namespace, system=SYSTEM_NAME, hostpath=HOST_PATH)
        self.create_pvc_yaml_from_template(CONF_PATH, tdb_namespace, system=SYSTEM_NAME, hostpath=HOST_PATH)

        # PV, PVC 생성
        if self.deploy_yaml(self.get_pv_filename(CONF_PATH, namespace=tdb_namespace)):
            print("Persistent volume is created.")
        else:
            raise Exception("The requested persistent volume already existed.")

        if self.deploy_yaml(self.get_pvc_filename(CONF_PATH, namespace=tdb_namespace)):
            print("Persistent volume claim is created.")
        else:
            raise Exception("The requested persistent volume claim already existed.")

##################################################################################################################
if __name__ == "__main__":
    tdb_ml_initializer = TrainDBMLInitializer('sungsoo')
    # tdb_ml_initializer.create_namespace(namespace='sungsoo')
    # tdb_ml_initializer.init('sungsoo')
    tdb_ml_initializer.delete_namespace('sungsoo')
