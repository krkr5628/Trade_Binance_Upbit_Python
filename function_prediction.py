import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

import torch
import torch.nn as nn


# 시퀀스 길이 설정
sequence_length = 60

def time_series(data) :
    # open_time 열을 datetime 형식으로 변환
    data['open_time'] = pd.to_datetime(data['open_time'], errors='coerce')

    # time 열을 분 단위로 변환
    data['time'] = data['open_time'].dt.hour * 60 + data['open_time'].dt.minute

    # 무한대 값을 NaN으로 대체
    data = data.replace([np.inf, -np.inf], np.nan)

    # NaN 대체와 정규화 작업을 파이프라인으로 결합
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', MinMaxScaler())
    ])

    # 데이터에 파이프라인 적용
    data = pipeline.fit_transform(data)

    # 예측 데이터를 시퀀스 형태로 변환하는 함수
    def create_sequences_for_prediction(data, sequence_length):
        num_sequences = len(data) - sequence_length + 1
        sequences = np.empty((num_sequences, sequence_length, data.shape[1]), dtype=data.dtype)
        for i in range(num_sequences):
            sequences[i] = data[i:i + sequence_length]
        return sequences

    # 예측용 시퀀스 데이터 생성
    X_test_seq = create_sequences_for_prediction(data, sequence_length)

    return X_test_seq

def model_load(X_test_seq, path) :
    # 모델 로드
    class TCNModel(nn.Module):
        def __init__(self, input_channels, num_channels, kernel_size=2, dropout=0.2):
            super(TCNModel, self).__init__()
            self.tcn = nn.Conv1d(input_channels, num_channels, kernel_size, padding=kernel_size // 2)
            self.relu = nn.ReLU()
            self.dropout = nn.Dropout(dropout)
            self.fc = nn.Linear(num_channels, 1)

        def forward(self, x):
            x = x.transpose(1, 2)  # (batch_size, seq_len, input_channels) -> (batch_size, input_channels, seq_len)
            y1 = self.tcn(x)
            y1 = self.relu(y1)
            y1 = self.dropout(y1)
            y1 = y1[:, :, -1]
            o = self.fc(y1)
            return o

    # 입력 차원 확인 및 설정
    input_channels = X_test_seq.shape[2]

    # 모델 설정
    num_channels = 64
    model = TCNModel(input_channels, num_channels)

    # 모델 로드
    #model_path = '/content/drive/MyDrive/Data/Model/SOL60_INDICATOR3_TCN_v7.pth'
    model.load_state_dict(torch.load(path))
    model.eval()

    return model.eval()


def predction(model, X_test_seq) :

    # 테스트 데이터 텐서로 변환
    X_test_tensor = torch.tensor(X_test_seq, dtype=torch.float32)

    # 예측 수행
    batch_size = 1024  # 예: 1024개의 샘플을 한 번에 처리
    predictions = []

    model.eval()
    with torch.no_grad():
        for i in range(0, X_test_tensor.size(0), batch_size):
            batch = X_test_tensor[i:i + batch_size]
            batch_predictions = torch.sigmoid(model(batch)).squeeze().numpy()
            predictions.append(batch_predictions)

    # 모든 배치 결과를 하나의 배열로 병합
    predictions = np.concatenate(predictions)

    # 이진 분류로 변환
    predictions = (predictions > 0.5).astype(int)

    # 예측 결과를 데이터프레임에 추가
    data['prediction_Transformer'] = np.nan  # 예측 결과를 담을 열을 초기화
    data.iloc[sequence_length - 1:sequence_length - 1 + len(predictions),
    data.columns.get_loc('prediction_Transformer')] = predictions

    return predictions
