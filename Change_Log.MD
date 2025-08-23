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
