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

import sys
sys.path.append('../metadata/')

# 필요한 라이브러리 import
from typing import List

from kubernetes import client 
from kubernetes import config 
from kubernetes import utils 
from kubernetes.client import V1PodTemplateSpec 
from kubernetes.client import V1ObjectMeta 
from kubernetes.client import V1PodSpec 
from kubernetes.client import V1Container 
from kubernetes.client import V1ResourceRequirements 
from kubernetes.client import V1PersistentVolumeClaimVolumeSource 
from kubernetes.client import V1Volume
from kubernetes.client import V1VolumeMount

from kserve import KServeClient
from kserve import constants
from kserve import utils
from kserve import V1beta1InferenceService
from kserve import V1beta1InferenceServiceSpec
from kserve import V1beta1PredictorSpec
from kserve import V1beta1TorchServeSpec
from kserve import Predictor, KServe

class ModelServer:
    def __init__(self, model_type: str, model_name: str, model_uri: str):
        # 모델 이름과 모델 uri를 인자로 받아 Predictor 객체 생성
        self.modeltype = model_type
        self.modelname = model_name
        self.pod_name = "traindb-ml-serve-" + model_type + "-" + model_name
        self.kserve = KServeClient()
        self.predictor = Predictor(model_name=model_name, model_uri=model_uri)

    def predict(self, inputs: List):
        # 입력값을 Predictor 객체의 predict 메소드에 전달하여 예측값 반환

        return self.predictor.predict(inputs)
    
    def register_serving(self, nspace: str, uri_storage: str):
        isvc = V1beta1InferenceService(
    		api_version=constants.KSERVE_V1BETA1,
            kind=constants.KSERVE_KIND,
            metadata=V1ObjectMeta(
                name=self.pod_name,
                labels={"system":"traindb", "subsystem":"ml","podtype":"serve","modeltype":self.modeltype,"modelname":self.modelname},
                namespace=nspace
                ),
                spec=V1beta1InferenceServiceSpec(
    			  predictor=V1beta1PredictorSpec(
    				    pytorch=V1beta1TorchServeSpec(storage_uri=uri_storage))))
        
        self.kserve.create(isvc, namespace=nspace)
        self.kserve.get(self.pod_name, namespace=nspace)
        self.kserve.get(self.pod_name, namespace=nspace, watch=True, timeout_seconds=120)
        self.kserve.wait_isvc_ready(self.pod_name, namespace=nspace)

if __name__ == '__main__':
    # 모델 서버 생성
    server = ModelServer(model_name='my_model', model_uri='http://localhost:8080')

    # 입력값 리스트 생성
    inputs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    # 모델 예측 실행
    outputs = server.predict(inputs)

    # 예측 결과 출력
    print(outputs)

# # 필요한 라이브러리 import
# import kfserving
# from typing import List, Dict
# import numpy as np
# import json

# # 모델 클래스 생성
# class TrainDBModel(kfserving.KFModel):
    
#     # 모델 초기화 함수
#     def __init__(self, name: str):
#         super().__init__(name)
        
#     # 모델 로드 함수
#     def load(self) -> None:
#         # 모델 로드 코드 작성
#         pass
    
#     # 모델 추론 함수
#     def predict(self, request: Dict) -> Dict:
#         # 입력 데이터 전처리
#         data = request['instances']
#         data = np.array(data)
        
#         # 모델 추론 코드 작성
#         result = None
        
#         # 결과값 후처리
#         return {'predictions': result.tolist()}
    
# # 모델 서빙을 위한 KFServer 객체 생성
# server = kfserving.KFServer()

# # 모델 등록
# server.register_model('my-model', TrainDBModel('my-model'))

# # 모델 서빙 시작
# server.start({'HTTP_PORT': '8080'})













