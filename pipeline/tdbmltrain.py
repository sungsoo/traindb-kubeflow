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

# 필요한 라이브러리 import
import kfp
from kfp import dsl
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op

# 훈련 스크립트를 실행할 컨테이너 이미지 지정
BASE_IMAGE = "pytorch/pytorch:1.7.1-cuda11.0-cudnn8-runtime"

# 훈련 스크립트를 실행할 함수 정의
@func_to_container_op
def train(
    data_path: InputPath(),  # 입력 데이터 경로
    model_path: OutputPath(),  # 모델 저장 경로
    epochs: int,  # 에폭 수
    learning_rate: float,  # 학습률
    batch_size: int,  # 배치 크기
):
    import torch
    from torch.utils.data import DataLoader
    from torchvision.datasets import MNIST
    from torchvision.transforms import ToTensor
    from torch import nn, optim

    # 데이터 로드
    train_data = MNIST(data_path, train=True, download=True, transform=ToTensor())
    test_data = MNIST(data_path, train=False, download=True, transform=ToTensor())

    # 데이터 로더 생성
    train_loader = DataLoader(train_data, batch_size=batch_size)
    test_loader = DataLoader(test_data, batch_size=batch_size)

    # 모델 정의
    class Net(nn.Module):
        def __init__(self):
            super(Net, self).__init__()
            self.conv1 = nn.Conv2d(1, 32, 3, 1)
            self.conv2 = nn.Conv2d(32, 64, 3, 1)
            self.dropout1 = nn.Dropout2d(0.25)
            self.dropout2 = nn.Dropout2d(0.5)
            self.fc1 = nn.Linear(9216, 128)
            self.fc2 = nn.Linear(128, 10)

        def forward(self, x):
            x = self.conv1(x)
            x = nn.functional.relu(x)
            x = self.conv2(x)
            x = nn.functional.relu(x)
            x = nn.functional.max_pool2d(x, 2)
            x = self.dropout1(x)
            x = torch.flatten(x, 1)
            x = self.fc1(x)
            x = nn.functional.relu(x)
            x = self.dropout2(x)
            x = self.fc2(x)
            output = nn.functional.log_softmax(x, dim=1)
            return output

    # 모델 초기화
    model = Net()

    # 손실 함수와 옵티마이저 정의
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 훈련
    for epoch in range(epochs):
        for i, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    # 모델 저장
    torch.save(model.state_dict(), model_path)

# 파이프라인 정의
@dsl.pipeline(name="pytorch-mnist")
def pytorch_mnist(
    data_path: str = "/mnt/data/mnist",
    model_path: str = "/mnt/model/model.pt",
    epochs: int = 10,
    learning_rate: float = 0.001,
    batch_size: int = 64,
):
    train_op = train(data_path, model_path, epochs, learning_rate, batch_size)

# 파이프라인 실행
if __name__ == "__main__":
    kfp.compiler.Compiler().compile(pytorch_mnist, "pytorch-mnist.tar.gz")

