# pyCameraControl

基於 Python 和 Tkinter 開發的專業相機控制介面，支援 macOS 和 Windows 雙平台：
- **macOS 版本**: 使用 gPhoto2 實現完整相機控制
- **Windows 版本**: 透過 digiCamControl 實現相機操作

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-Source%20Available-orange.svg)

## 功能特色

### 核心功能
- **即時相機連接**: 自動偵測並連接相容相機
- **智慧參數檢測** (macOS): 自動檢測相機支援的參數，動態更新介面選項
- **專業控制** (macOS): 完整的曝光三角、測光、對焦、白平衡手動控制
- **拍攝模式**: 單張拍攝、連拍模式（可設定間隔時間）
- **Tethered 拍攝** (macOS): 支援無 SD 卡直接傳輸到電腦
- **即時預覽**: 拍攝後立即預覽，支援縮放控制
- **檔案管理**: 有組織的照片儲存、自訂檔案命名、刪除最後拍攝照片
- **響應式介面**: 優化的UI響應速度，設定變更即時反饋

### 相機控制 (macOS 版本)
- **智慧曝光設定**
  - ISO 感光度: 自動檢測相機支援範圍
  - 光圈值: 依據鏡頭規格動態載入
  - 快門速度: 相機支援的完整範圍
  - 曝光補償: 依相機型號自動調整
- **智慧相機設定**
  - 白平衡: 依相機型號顯示實際選項 (例如: 自動(氣氛優先)、自動(白色優先)、色溫設定等)
  - 影像品質: 動態顯示 RAW、C-RAW、JPEG 等相機支援格式
  - 測光模式: 依相機支援動態載入
  - 對焦模式: 相機專屬選項自動檢測
  - 拍攝目標: 支援 SD 卡或內部記憶體/電腦 (Tethered 模式)

### 拍攝模式
- **單張拍攝**: 單次快門拍攝
- **連拍模式**: 1-999 張連續拍攝，可設定拍攝間隔時間 (0-3600 秒)

### 使用者介面
- 簡潔的現代化介面設計
- 即時連接狀態顯示
- 多張拍攝進度追蹤
- 直觀的檔案瀏覽器整合
- 響應式布局與分區組織
- 相機設定檢視器 (macOS)
- 快速刪除最後拍攝照片
- 一鍵開啟儲存資料夾

## 螢幕截圖

應用程式採用三面板布局設計：
- **左面板**: 相機連接、曝光設定與相機參數
- **中面板**: 拍攝控制與拍攝模式
- **右面板**: 影像預覽與檔案管理

## 安裝說明

### 系統需求
- Python 3.8 或更高版本
- 支援 USB 連接的相容相機

### macOS 版本

#### 系統相依性
```bash
# 透過 Homebrew 安裝 gphoto2
brew install gphoto2
```

#### Python 套件
```bash
pip install gphoto2 pillow
```

### Windows 版本

#### 系統相依性
1. 下載並安裝 [digiCamControl](http://digicamcontrol.com/)
2. 確保 digiCamControl 應用程式已安裝並可正常執行
3. 確認 `CameraControlRemoteCmd.exe` 可在系統中存取

#### Python 套件
```bash
pip install pillow
```

**注意**: Windows 版本使用 digiCamControl 作為相機後端，功能聚焦於拍攝控制，不包含相機參數設定功能。

## 使用方法

### macOS 版本

1. **啟動應用程式**
   ```bash
   python main.py
   ```

2. **連接相機**
   - 透過 USB 連接相機
   - 點擊「Connect Camera」按鈕
   - 等待自動偵測並建立連接
   - 程式會自動檢測相機支援的參數

3. **查看相機設定**
   - 連接後點擊「Show Camera Settings」查看完整參數列表
   - 所有下拉選單會自動更新為相機實際支援的選項

4. **設定參數**
   - 調整曝光設定: ISO、光圈值、快門速度、曝光補償
   - 設定相機功能: 白平衡、影像品質、測光模式、對焦模式
   - 選擇拍攝目標: SD 卡或內部記憶體 (Tethered 模式)
   - 選擇拍攝模式 (單張/連拍)
   - 設定儲存位置與檔案名稱前綴

5. **拍攝照片**
   - 點擊「CAPTURE」按鈕或使用設定的拍攝模式
   - 在狀態區域監控進度
   - 在預覽面板中查看拍攝的影像
   - 可使用「Delete Last」刪除最後一張照片
   - 可使用「Browse」開啟儲存資料夾

### Windows 版本

1. **啟動應用程式**
   ```bash
   # 確保 digiCamControl 應用程式正在執行
   python main_windows.py
   ```

2. **連接相機**
   - 在 digiCamControl 應用程式中連接相機
   - 在 pyCameraControl 中點擊「Connect Camera」按鈕
   - 等待連接確認

3. **設定拍攝參數**
   - 選擇拍攝模式 (單張/連拍)
   - 設定連拍數量和間隔時間（如需要）
   - 設定儲存位置與檔案名稱前綴
   - **注意**: 相機參數（ISO、光圈等）需在 digiCamControl 應用程式中調整

4. **拍攝照片**
   - 點擊「CAPTURE」按鈕
   - 在狀態區域監控進度
   - 在預覽面板中查看拍攝的影像
   - 可使用「Delete Last」刪除最後一張照片
   - 可使用「Browse」開啟儲存資料夾

## 支援相機

### macOS 版本
支援 gPhoto2 相容的相機，包括：
- Canon EOS 系列 (包含最新的 C-RAW 格式支援)
- Nikon D/Z 系列
- Sony Alpha 系列
- Fujifilm X 系列
- 其他多種 DSLR 和無反光鏡相機

請查看 [gPhoto2 相容性清單](http://gphoto.org/proj/libgphoto2/support.php) 確認您的相機型號。

### Windows 版本
支援 digiCamControl 相容的相機，包括：
- Canon EOS 系列
- Nikon D 系列
- 其他支援 PTP/MTP 協定的相機

請查看 [digiCamControl 相容性清單](http://digicamcontrol.com/cameras) 確認您的相機型號。

## 設定選項

### 動態設定檢測 (macOS 版本)
程式會自動檢測您的相機並載入：
- 實際支援的 ISO 範圍
- 鏡頭光圈範圍
- 可用的快門速度
- 相機特有的白平衡選項
- 支援的檔案格式 (JPEG/RAW/C-RAW 等組合)
- 測光與對焦模式
- Tethered 拍攝模式 (直接儲存至電腦)

### 檔案管理
- **預設儲存位置**: `./photos/`
- **檔案名稱前綴**: `IMG`
- 支援自訂儲存目錄
- 時間戳記自動命名
- 連拍檔案編號管理

## 疑難排解

### macOS 版本

#### 無法偵測到相機
- 確保相機處於 PC/大容量儲存模式
- 檢查 USB 連接
- 確認相機與 gPhoto2 的相容性
- 嘗試斷開並重新連接相機
- 確認 gPhoto2 已正確安裝：`gphoto2 --version`

#### 參數設定問題
- 使用程式內建的「Show Camera Settings」功能查看支援參數
- 某些參數需要相機處於特定模式（如M模式）才能調整
- 程式會自動跳過不支援的參數設定

#### Tethered 模式問題
- 確認相機支援無 SD 卡拍攝
- 檢查「Capture Target」設定是否已切換至內部記憶體
- 部分相機可能需要在相機選單中啟用 PC 連接模式

### Windows 版本

#### 無法連接相機
- 確保 digiCamControl 應用程式正在執行
- 在 digiCamControl 中確認相機已成功連接
- 檢查 `CameraControlRemoteCmd.exe` 是否可執行
- 嘗試重新啟動 digiCamControl

#### 拍攝失敗
- 確認相機在 digiCamControl 中可正常拍攝
- 檢查儲存路徑是否有寫入權限
- 確保相機不是處於睡眠模式

### 共通問題

#### 介面響應問題
- 程式已優化響應速度，設定變更會即時顯示
- 如遇到延遲，請檢查相機連接狀態
- 嘗試重新連接相機

#### 預覽圖片無法顯示
- 確認照片已成功儲存至指定資料夾
- 檢查圖片格式是否為支援的格式 (JPG/JPEG)
- 對於 RAW 格式，程式會嘗試顯示內嵌的預覽圖

## 開發資訊

### 技術特色
- **跨平台設計**: 支援 macOS 和 Windows 雙平台
- **智慧參數檢測系統** (macOS): 自動檢測相機功能並動態更新介面
- **後端抽象化** (Windows): 使用 `camera_backends.py` 實現相機後端抽象
- **優化的UI響應機制**: 50ms 更新間隔，即時反饋
- **多線程拍攝處理**: 非阻塞式拍攝操作
- **佇列式通訊**: 使用 Queue 實現執行緒間安全通訊

### 專案結構
```
pyCameraControl/
├── main.py              # macOS 版本主程式 (gPhoto2)
├── main_windows.py      # Windows 版本主程式 (digiCamControl)
├── camera_backends.py   # Windows 相機後端抽象層
├── README.md            # 專案說明文件
└── photos/              # 預設照片儲存目錄
```

### 技術棧
- **GUI 框架**: Tkinter
- **影像處理**: Pillow (PIL)
- **相機控制**:
  - macOS: gPhoto2 Python bindings
  - Windows: digiCamControl Remote Utility (subprocess)
- **並行處理**: Python threading 和 queue

## 更新日誌

### 最新版本
- **新增 Windows 平台支援**: 透過 digiCamControl 實現 Windows 版本
- **移除間隔拍攝模式**: 簡化拍攝模式，間隔時間整合至連拍功能
- **新增照片管理功能**:
  - 刪除最後一張照片功能
  - 一鍵開啟儲存資料夾
- **優化相機連接**: 改進相機連接穩定性
- **修復設定問題**: 解決參數設定相關問題

### 先前版本
- 智慧相機參數檢測
- 優化介面響應速度 (50ms 更新間隔)
- 動態參數選單更新
- 相機設定檢視器
- 移除固定預設值，完全依照相機規格
- Tethered 拍攝模式支援

## 致謝

- macOS 版本使用 [gPhoto2](http://gphoto.org/) 進行相機通訊
- Windows 版本使用 [digiCamControl](http://digicamcontrol.com/) 作為相機後端
- UI 介面採用 Python Tkinter
- 影像處理使用 [Pillow](https://pillow.readthedocs.io/)

## 作者

**Sean Tsai**  
seantsai.work@gmail.com

## 授權條款

本專案採用 **Source Available License**，允許個人、教育、研究及非商業用途使用。

### 重要提醒

- **允許**: 個人使用、教育、研究、學習、查看原始碼
- **允許**: 修改程式碼供個人或非商業用途
- **禁止**: 任何商業用途（需取得書面授權）
- **禁止**: 公開散布修改版本（需取得許可）

這**不是**開源授權（Open Source Initiative 定義），原始碼僅供查看、學習及個人/非商業用途。

### 商業授權

如需商業使用，包括但不限於：
- 銷售、授權或作為產品/服務的一部分
- 使用本軟體提供付費服務（SaaS、諮詢、託管等）
- 嵌入到任何商業產品或應用程式中

請聯絡作者取得商業授權：
**Email**: seantsai.work@gmail.com

### 完整授權條款

詳細授權條款請參閱專案根目錄的 [LICENSE](LICENSE) 檔案。

```
Source Available License – pyCameraControl (2025)
Copyright (c) 2025 Sean Tsai. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software for personal, educational, research, or non-commercial purposes
only, subject to the conditions in the LICENSE file.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```