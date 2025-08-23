---
**작성 원칙 (Writing Principles)**

1.  **목적 중심 (Purpose-Driven)**: 모든 문서는 명확한 목적을 가지며, 독자가 해당 목적을 쉽게 달성할 수 있도록 구성합니다.
2.  **구조적 작성 (Structured Writing)**: `Markdown`의 제목, 목록, 코드 블록 등을 활용하여 정보를 체계적으로 구조화합니다.
3.  **최신성 유지 (Up-to-Date)**: 코드베이스의 변경사항이 발생하면, 관련된 모든 문서를 신속하게 업데이트하여 최신 상태를 유지합니다.
4.  **명확하고 간결한 표현 (Clarity and Brevity)**: 전문 용어 사용을 최소화하고, 누구나 이해하기 쉬운 명확하고 간결한 언어로 작성합니다.
5.  **일관성 (Consistency)**: 전체 문서에서 통일된 용어와 서식을 사용하여 일관성을 유지합니다.
6.  **항목별 버전 관리 (Item-level Versioning)**: 각 문서 내의 주요 섹션(항목)은 개별적으로 버전을 관리합니다. 예를 들어, `Progress.md`의 '개발 목표'와 '기능 구성'은 서로 다른 버전을 가질 수 있습니다. 내용에 중요한 변경이 있을 때마다 해당 항목의 버전(예: v1.0.0 -> v1.1.0)을 업데이트하여 변경 이력을 명확히 추적합니다.
---

# Changelog

## [1.1.0] - 2025-08-23

### Changed
- **Improved Error Handling**: Added comprehensive `try-except` blocks to `function.py` for all network requests and file I/O operations to prevent crashes and provide better error messages.
- **Refactored API Functions**: Modified functions in `function.py` (e.g., `Market_Data_Specific`, `order_possible`) to return DataFrames instead of printing to the console, improving modularity. Created a helper function `_get_auth_headers` to reduce code duplication.
- **Simplified Candle Loading**: Refactored the `Candle_initial_update` function in `function_complex.py` to remove complex and unused code, simplifying the initial data loading process.
- **Enhanced WebSocket Logging**: Improved the `function_real.py` module to log WebSocket connection status (connect, close, errors, reconnect attempts) directly to the UI for better user feedback.
- **Code Clarity**: Added warning comments in `function_feature.py` for placeholder implementations (`calculate_rvi`) and clarified custom logic (`calculate_vr`). Added comments to `function_complex.py` to explain the button signal/slot reconnection logic.

## [1.0.0] - 2025-08-23

### Added
- `PROGRAM_STRUCTURE.md`: A new document that explains the overall architecture of the program and the role of each file.
- Added detailed Korean comments and docstrings to all Python source files (`Main.py`, `function.py`, `function_complex.py`, `function_real.py`, `function_feature.py`) to improve code readability and maintainability.

### Changed
- Initial project setup for versioning.
