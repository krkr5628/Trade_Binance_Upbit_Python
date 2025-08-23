---
**작성 원칙 (Writing Principles)**

1.  **목적 중심 (Purpose-Driven)**: 모든 문서는 명확한 목적을 가지며, 독자가 해당 목적을 쉽게 달성할 수 있도록 구성합니다.
2.  **구조적 작성 (Structured Writing)**: `Markdown`의 제목, 목록, 코드 블록 등을 활용하여 정보를 체계적으로 구조화합니다.
3.  **최신성 유지 (Up-to-Date)**: 코드베이스의 변경사항이 발생하면, 관련된 모든 문서를 신속하게 업데이트하여 최신 상태를 유지합니다.
4.  **명확하고 간결한 표현 (Clarity and Brevity)**: 전문 용어 사용을 최소화하고, 누구나 이해하기 쉬운 명확하고 간결한 언어로 작성합니다.
5.  **일관성 (Consistency)**: 전체 문서에서 통일된 용어와 서식을 사용하여 일관성을 유지합니다.
6.  **항목별 버전 관리 (Item-level Versioning)**: 각 문서 내의 주요 섹션(항목)은 개별적으로 버전을 관리합니다. 예를 들어, `Progress.md`의 '개발 목표'와 '기능 구성'은 서로 다른 버전을 가질 수 있습니다. 내용에 중요한 변경이 있을 때마다 해당 항목의 버전(예: v1.0.0 -> v1.1.0)을 업데이트하여 변경 이력을 명확히 추적합니다.
---

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

## 3. Development Progress (v1.2.0)

### Checklist & Status

#### Phase 1: Core Infrastructure & Upbit Integration (완료)
- [x] **GUI 기본 구조 설계 (End)**
    - [x] PySide6를 이용한 메인 윈도우 및 기본 레이아웃 구성
    - [x] 데이터 표시를 위한 테이블 뷰, 로그 출력을 위한 텍스트 브라우저 등 위젯 배치
- [x] **Upbit API 연동 (End)**
    - [x] `function.py`: 계좌 조회, 주문 등 REST API 호출 함수 구현
    - [x] `function_real.py`: 실시간 시세 수신을 위한 WebSocket 연동 구현
    - [x] `function_complex.py`: API 데이터를 UI에 맞게 가공 및 표시하는 비즈니스 로직 구현
- [x] **주요 거래 기능 구현 (End)**
    - [x] 계좌 정보(보유자산, 평가액) 조회 및 표시
    - [x] 미체결/체결 주문 내역 조회 및 표시
    - [x] 지정가/시장가 매수 주문 기능 구현 (최소 주문 금액 등 예외처리 포함)
    - [x] 미체결 주문 선택 및 취소 기능 구현

#### Phase 2: Machine Learning Pipeline (진행중)
- [x] **데이터 처리 및 피처 엔지니어링 (End)**
    - [x] `function_feature.py`: `ta` 라이브러리를 활용한 100개 이상의 기술적 보조지표 생성 기능 구현
- [x] **예측 파이프라인 구조 구현 (End)**
    - [x] 1분마다 새로운 캔들 데이터에 맞춰 기술적 지표를 업데이트하는 로직 구현
    - [x] 예측 모델의 출력을 UI에 표시하는 기능 구현 (현재 더미 모델)
- [ ] **실제 예측 모델 개발 (Doing)**
    - [ ] `Scikit-learn` 또는 `PyTorch`를 이용한 가격 예측 모델 설계 및 학습
    - [ ] 학습된 모델 파일 저장 및 로드 기능 구현
    - [ ] `function_feature.get_prediction` 함수를 실제 모델 예측 코드로 교체

#### Phase 3: Binance Futures Integration (진행중)
- [x] **기본 API 구조 설계 (End)**
    - [x] `function_binance.py` 파일 생성 및 선물 거래 관련 함수 플레이스홀더 추가
- [ ] **Binance API 기능 구현 (Doing)**
    - [ ] 바이낸스 선물 계좌 잔고 조회 기능 구현
    - [ ] 바이낸스 선물 주문(시장가/지정가) 실행 기능 구현
    - [ ] 바이낸스 미체결 주문 조회 및 취소 기능 구현
    - [ ] 바이낸스 실시간 데이터 수신을 위한 WebSocket 연동

### Progress
- **Total Progress: 14/21 (약 67%)**
