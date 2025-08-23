# Development Progress

## 1. Development Goal (v1.0.0)
- Upbit & Binance API를 활용하여 현물 및 선물 거래를 지원하는 자동 매매 프로그램 개발.
- 단순 지표 기반이 아닌, 머신러닝/딥러닝 예측 모델을 탑재하여 매매 결정의 정확성을 높이는 것을 목표로 함.

## 2. Feature Composition (v1.1.0)
- **GUI**: PySide6 기반의 사용자 인터페이스
- **API 연동**:
    - Upbit REST API (계좌 조회, 주문 실행/취소, 마켓 정보 조회)
    - Upbit WebSocket API (실시간 시세 수신)
    - **(신규)** Binance API 기본 구조 (선물 거래 기능 확장 기반)
- **주요 기능**:
    - 계좌 정보: 보유 자산 및 평가액 실시간 표시
    - 주문 관리: 미체결/체결 내역 조회, 신규 주문(최소금액 체크 등 개선), 주문 취소
    - 시세 표시: 현재가, 등락률, 캔들 차트(1분봉) 표시
- **데이터 처리**:
    - `ta` 라이브러리를 활용한 다수의 기술적 보조지표 생성 엔진
- **예측 모델**:
    - **(신규)** 더미 예측 모델을 포함한 전체 예측 파이프라인 구조 구현
    - (예정) Scikit-learn, PyTorch 기반의 실제 가격 예측 모델 연동

## 3. Development Progress (v1.1.0)

### Checklist & Status
- [x] **Core**: GUI 기본 구조 설계 (End)
- [x] **Core**: Upbit API 연동 (계좌, 주문) (End)
- [x] **Core**: Upbit WebSocket 연동 (실시간 시세) (End)
- [x] **Feature**: 계좌 정보 표시 기능 (End)
- [x] **Feature**: 주문 내역(미체결/체결) 표시 기능 (End)
- [x] **Feature**: 주문 실행/취소 기능 (개선) (End)
- [x] **Feature**: 캔들 데이터 표시 기능 (End)
- [x] **Feature**: 기술적 보조지표 생성 기능 (End)
- [x] **ML**: 예측 파이프라인 구현 (End)
- [x] **Expansion**: Binance API 기본 구조 추가 (End)
- [ ] **ML**: 실제 예측 모델 학습 및 구현 (Doing)
- [ ] **Expansion**: Binance 선물 API 기능 구현 (Doing)


### Progress
- **Total Progress: 10/12 (약 83%)**
