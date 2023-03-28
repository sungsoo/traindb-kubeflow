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

import os # os 모듈 import
import subprocess # subprocess 모듈 import


# 현재 디렉토리에서 소스 코드 파일을 찾는다.
for file in os.listdir():
    if file.endswith(".py"):
        source_file = file

# 도커 이미지를 생성할 때 사용할 베이스 이미지를 정한다.
base_image = "python:3.8-slim"

# 도커 파일을 생성할 경로와 이름을 정한다.
dockerfile_path = "./Dockerfile"

# 도커 파일을 생성한다.
with open(dockerfile_path, "w") as f:
    # 베이스 이미지를 사용한다는 것을 명시한다.
    f.write(f"FROM {base_image}\n\n")
    
    # 소스 코드 파일을 도커 이미지 내부로 복사한다.
    f.write("COPY " + source_file + " /app/\n\n")
    
    # 필요한 라이브러리를 설치한다.
    f.write("RUN pip install --no-cache-dir -r /app/requirements.txt\n\n")
    
    # 컨테이너가 시작될 때 실행할 명령어를 정한다.
    f.write("CMD [\"python\", \"/app/" + source_file + "\"]\n")

# 현재 디렉토리에 있는 모든 파일과 디렉토리를 리스트로 반환
files = os.listdir()

# requirements.txt 파일 생성
with open('requirements.txt', 'w') as f:
    # 현재 디렉토리에서 실행 가능한 pip 명령어 실행
    result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE)
    # 실행 결과를 requirements.txt 파일에 작성
    f.write(result.stdout.decode('utf-8'))



# Dockerfile Generator라는 프로그램을 사용할 수 있습니다. 
# 예를 들어, Python 소스 코드를 Docker 이미지로 빌드하기 위한 Dockerfile을 생성하려면, 
# Dockerfile Generator를 사용하여 필요한 모든 구성 요소를 지정하고 Dockerfile을 자동으로 생성할 수 있습니다. 
# 이를 통해 Dockerizing your Python application의 작업을 보다 쉽게 수행할 수 있습니다.

# Dockerfile Generator API를 이용하여 자동화된 방식으로 Docker 이미지를 생성하는 구체적인 예를 들어보겠습니다.

# 1. Flask 어플리케이션을 Docker 이미지로 빌드하는 경우:

# ```python
# import requests

# app_name = 'my-flask-app'
# app_version = 'v1'
# dockerfile_url = 'https://dockerfile-generator.com/api/dockerfile/flask'
# params = {
#     'app_name': app_name,
#     'app_version': app_version,
#     'requirements': 'requirements.txt',
#     'entry_point': 'app.py',
#     'port': 5000
# }

# # Dockerfile 생성 요청
# response = requests.post(dockerfile_url, params=params)

# # 생성된 Dockerfile 다운로드
# dockerfile = response.content

# # Dockerfile을 이용하여 Docker 이미지 빌드
# build_url = 'https://dockerfile-generator.com/api/build'
# files = {'dockerfile': dockerfile}
# params = {'t': f'{app_name}:{app_version}'}
# response = requests.post(build_url, files=files, params=params)

# # 빌드된 Docker 이미지 다운로드
# image_url = f'https://dockerfile-generator.com/images/{app_name}:{app_version}'
# response = requests.get(image_url)
# image = response.content
# ```

# 2. Django 어플리케이션을 Docker 이미지로 빌드하는 경우:

# ```python
# import requests

# app_name = 'my-django-app'
# app_version = 'v1'
# dockerfile_url = 'https://dockerfile-generator.com/api/dockerfile/django'
# params = {
#     'app_name': app_name,
#     'app_version': app_version,
#     'requirements': 'requirements.txt',
#     'entry_point': 'manage.py',
#     'port': 8000
# }

# # Dockerfile 생성 요청
# response = requests.post(dockerfile_url, params=params)

# # 생성된 Dockerfile 다운로드
# dockerfile = response.content

# # Dockerfile을 이용하여 Docker 이미지 빌드
# build_url = 'https://dockerfile-generator.com/api/build'
# files = {'dockerfile': dockerfile}
# params = {'t': f'{app_name}:{app_version}'}
# response = requests.post(build_url, files=files, params=params)

# # 빌드된 Docker 이미지 다운로드
# image_url = f'https://dockerfile-generator.com/images/{app_name}:{app_version}'
# response = requests.get(image_url)
# image = response.content
# ```

# 위의 코드는 Flask와 Django 어플리케이션을 Docker 이미지로 빌드하는 구체적인 예시입니다. 
# Dockerfile Generator API를 이용하여 다른 프레임워크나 언어에 대해서도 Docker 이미지를 자동화된 방식으로 생성할 수 있습니다.