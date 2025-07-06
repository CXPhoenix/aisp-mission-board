# AiSP Mission Board

![Version](https://img.shields.io/badge/version-v0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-green.svg)

> [!NOTE]
> Author: @CXPhoenix
>
> **注意**: 本專案目前處於開發階段，部分功能尚未完全實作。請參考下方的 TODO 清單瞭解開發進度。

---

## 專案簡介

AiSP Mission Board 是為人工智慧學生計畫 (Artificial Intelligence Student Program) 設計的任務管理系統。採用 FastAPI 框架搭配 MongoDB 資料庫，提供完整的任務管理、使用者管理及遊戲化功能。

### 核心功能

- 🎯 **任務管理系統**：使用者可以瀏覽、接受並完成任務
- 👥 **使用者管理**：完整的帳戶系統，包含角色權限管理
- 🏆 **遊戲化機制**：等級系統、Token 獎勵、任務進度追蹤
- 🛍️ **虛擬商城**：使用 Token 購買物品（開發中）
- 👨‍💼 **管理者介面**：任務審核、使用者管理、統計報表

## 技術架構

### 後端技術棧

- **Web Framework**: FastAPI
- **Database**: MongoDB with Beanie ODM
- **Template Engine**: Jinja2
- **Authentication**: Session-based
- **Package Manager**: uv
- **Containerization**: Docker & Docker Compose

### 前端技術棧

- **CSS Framework**: TailwindCSS
- **JavaScript**: Vanilla JS
- **Template**: Server-side rendering with Jinja2

## 系統需求

- Python 3.12+
- MongoDB 7.0+
- Docker & Docker Compose
- uv (Python package manager)

## 快速開始

### 1. 複製專案

```bash
git clone <repository-url>
cd aisp-mission-board
```

### 2. 設定環境變數

複製並設定環境變數檔案：

```bash
cp env.d/app.env.example env.d/app.env
cp env.d/mongo.env.example env.d/mongo.env
cp env.d/mongo-express.env.example env.d/mongo-express.env
cp env.d/cloudflare.env.example env.d/cloudflare.env
```

### 3. 啟動服務

```bash
# 啟動所有服務
docker-compose up -d

# 或只啟動應用程式和資料庫（開發用）
docker-compose up app mongo
```

### 4. 存取應用程式

- **應用程式主頁**: http://localhost:8000
- **MongoDB Express**: http://localhost:8081
- **API 文件**: http://localhost:8000/docs

## 專案結構

```
aisp-mission-board/
├── app/
│   ├── main.py              # FastAPI 應用程式進入點
│   ├── configs/             # 組態設定類別
│   ├── models/              # Beanie ODM 模型
│   │   ├── user.py         # 使用者模型
│   │   ├── mission.py      # 任務模型
│   │   ├── product.py      # 商品模型
│   │   ├── badge.py        # 成就模型（開發中）
│   │   └── record.py       # 紀錄模型（開發中）
│   ├── pages/               # 路由處理器
│   │   ├── auth_pages.py   # 認證相關路由
│   │   ├── mission_pages.py # 任務管理路由
│   │   ├── user_pages.py   # 使用者管理路由
│   │   ├── mall_pages.py   # 商城路由（開發中）
│   │   └── admin_pages/    # 管理者功能
│   ├── shared/             # 共用工具和中介軟體
│   │   ├── odm.py         # MongoDB 連線管理
│   │   ├── sessions.py    # Session 中介軟體
│   │   ├── dependencies.py # FastAPI 依賴注入
│   │   └── webpage.py     # 模板渲染工具
│   ├── templates/          # Jinja2 HTML 模板
│   └── public/            # 靜態資源
├── data/                   # 資料儲存目錄
│   ├── db/                # MongoDB 資料
│   └── logs/              # 應用程式日誌
├── env.d/                 # 環境變數設定檔案
├── docker-compose.yml     # Docker 服務組態
└── pyproject.toml         # Python 專案設定
```

## 資料庫架構

系統使用多個 MongoDB 資料庫：

- **userdb**: 使用者帳戶和擁有物品
- **malldb**: 商品目錄
- **recorddb**: 交易和使用紀錄
- **AiSP-Mission**: 任務資料和審核紀錄
- **App-Config**: 系統組態設定

## 使用者角色

- **USER**: 一般使用者，可以瀏覽和接受任務
- **MANAGER**: 管理員，具有審核任務的權限
- **ADMIN**: 系統管理員，具有完整的管理權限

## 開發命令

### 本地開發

```bash
# 安裝依賴
uv sync

# 啟動開發伺服器
uvicorn app.main:app --reload

# 啟動 TailwindCSS 監聽模式
npx tailwindcss -i ./app/public/input.css -o ./app/public/output.css --watch
```

### Docker 開發

```bash
# 啟動所有服務
docker-compose up -d

# 檢視日誌
docker-compose logs -f app

# 重新建立容器
docker-compose up --build

# 停止服務
docker-compose down
```

## API 文件

FastAPI 自動生成的 API 文件可在以下位置存取：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 功能狀態

### ✅ 已完成功能

- **使用者管理系統**
  - 使用者註冊、登入、登出
  - 角色權限管理
  - 使用者資料編輯
  - 批次匯入使用者

- **任務管理系統**
  - 任務瀏覽和搜尋
  - 任務接受和放棄
  - 任務提交和審核
  - 重複性任務支援
  - 任務等級限制

- **管理者功能**
  - 任務建立和編輯
  - 使用者管理
  - 任務審核系統
  - 統計報表

### 🚧 開發中功能

- **虛擬商城系統**
  - 商品瀏覽介面
  - 購物車功能
  - Token 交易系統
  - 使用者物品庫存管理

- **成就系統**
  - 成就條件定義
  - 成就解鎖邏輯
  - 成就展示介面

- **操作紀錄系統**
  - 管理者操作追蹤
  - 使用者行為記錄
  - 系統稽核軌跡

## TODO 清單

### 🔴 高優先度

1. **完整實作虛擬商城系統**
   - 商品瀏覽和搜尋介面 (`app/pages/mall_pages.py`)
   - 購物車功能
   - Token 交易處理
   - 使用者物品庫存管理
   - 商城模板實作 (`app/templates/mall/mall_board.html`)

2. **成就系統開發**
   - 成就模型完整實作 (`app/models/badge.py`)
   - 成就解鎖邏輯
   - 成就展示頁面

### 🟡 中優先度

3. **操作紀錄系統**
   - 管理者操作日誌 (`app/models/record.py`)
   - 使用者行為追蹤
   - 系統稽核報表

4. **系統最佳化**
   - 錯誤處理改善 (`app/main.py:66`)
   - 效能優化
   - 生產環境設定清理 (`app/main.py:73`)

### 🟢 低優先度

5. **使用者體驗改善**
   - 介面優化
   - 回應式設計改善
   - 載入效能提升

6. **文件和測試**
   - API 文件完善
   - 單元測試撰寫
   - 整合測試

## 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/新功能`)
3. 提交變更 (`git commit -am '新增: 某項功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 建立 Pull Request

## 版本歷史

### v0.1.0 (目前版本)
- 基礎架構建立
- 使用者管理系統
- 任務管理系統
- 管理者功能
- Docker 部署設定

## 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 聯絡資訊

如有任何問題或建議，請透過 GitHub Issues 聯繫我們。
