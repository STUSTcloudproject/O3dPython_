# RealSense Viewer 

## 概覽

RealSense Viewer 是一個基於 Intel RealSense 相機的圖形使用者介面（GUI）應用程式。它旨在即時顯示來自相機的各種影像串流（如深度圖、紅外圖和彩色圖），同時提供使用者介面以調整相機的設定。

## 架構

該專案採用模組化設計，分為幾個主要模組，如 GUI 設計、影像處理、RealSense 控制和應用邏輯，以確保代碼的可維護性和可擴展性。

### 主要組件

- **GUI ( `GUI.py` )**：構建應用程式的使用者介面，包括視窗、面板和可折疊面板等組件。該模組繼承於 `tkinter` 框架，不僅負責基礎的布局管理，還通過定義回調函數接口處理用戶的交互行為，支持事件驅動的架構模式。

- **CollapsiblePane ( `CollapsiblePane.py` )**：實現可折疊面板，用於在 GUI 中動態顯示和隱藏內容。透過用戶操作，可折疊面板能夠以動態方式展示或隱藏細節資訊。

- **ToggleSwitch ( `ToggleSwitch.py` )**：為 GUI 中的布林設定提供切換按鈕控制。該組件透過回調機制與應用邏輯層交互，將用戶操作轉換為應用中的相應事件和動作。

- **ImageProcessor ( `ImageProcessor.py` )**：負責影像的預處理，包括調整大小和顏色轉換。該模組作為處理 RealSense 相機原始數據與用戶界面展示之間的中介，確保影像數據能夠被有效處理和呈現。

- **SizeCalculator ( `SizeCalculator.py` )**：計算影像顯示的目標大小，維持特定的長寬比。

- **RealSense ( `RealSense.py` )**：封裝與 RealSense 相機交互的邏輯，包括配置、啟動和停止數據流。透過此模組，應用能夠靈活控制相機硬件，並根據實際需求調整相機設置。

- **MainApp ( `main.py` )**：應用程式的入口點和核心，整合所有上述組件。它負責初始化應用、處理應用層邏輯，並協調各組件間的交互。通過實施回調函數和採用事件驅動架構，`MainApp` 確保了應用的模組化、靈活性以及組件間的低耦合度。


### 設計決策

- **多線程**：為了保持 GUI 的響應性，與 RealSense 相機的交互和影像處理在後台線程中進行，於 `RealSense.py` 與 `main.py` 文件使用。
- **模組化**：通過將功能分解為專門的類和文件，專案可以更容易地理解、維護和擴展。
- **事件驅動**：使用者介面的互動基於事件驅動模型，藉由調用 `main.py` 文件裡提供的 `toggle_switch_changed` 方法，使得使用者操作直觀且響應迅速。

## 環境設置

本專案需要安裝 `pyrealsense2`、`numpy` 和 `Pillow`。您可以透過以下指令來安裝這些依賴：

```bash
pip install -r requirements.txt
```
## 啟動應用程式

啟動 RealSense Viewer 應用程式的步驟相對直接。在安裝了所有必要的依賴之後，您可以透過以下指令來運行應用程式：

1. 打開終端（在 macOS 或 Linux）或命令提示字元/PowerShell（在 Windows）。
2. 導航到包含專案檔案的目錄。
3. 執行下列指令來啟動應用程式：

```bash
python main.py

