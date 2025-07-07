# AiSP Mission Board

![Version](https://img.shields.io/badge/version-v0.6.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-green.svg)

> [!NOTE]
> Author: @CXPhoenix
>
> Version: 0.6.0
> 
> **注意**: 本專案目前處於開發階段，部分功能尚未完全實作。請參考下方的 TODO 清單瞭解開發進度。

---

## 專案簡介

AiSP Mission Board 是為復興高中 AI 資安學程 (FHSH AI & Cybersecurity Program) 設計的遊戲化任務管理系統。採用 FastAPI 框架搭配 MongoDB 資料庫，提供完整的任務管理、使用者管理及遊戲化功能。

### 核心功能

- 🎯 **任務管理系統**：使用者可以瀏覽、接受並完成任務
- 👥 **使用者管理**：完整的帳戶系統，包含角色權限管理
- 🏆 **遊戲化機制**：等級系統、Token 獎勵、任務進度追蹤
- 🛍️ **虛擬商城**：使用 Token 購買物品，包含實體商品申請功能
- 👨‍💼 **管理者介面**：任務審核、使用者管理、統計報表
- 🔄 **資料庫遷移系統**：自動化資料庫架構管理與 CLI 工具

## 技術架構

### 後端 Tech Stack

- **Web Framework**: FastAPI
- **Database**: MongoDB with Beanie ODM
- **Migration System**: Beanie ODM with CLI tools
- **Template Engine**: Jinja2
- **Authentication**: Session-based
- **Package Manager**: uv
- **Containerization**: Docker & Docker Compose

### 前端 Tech Stack

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
git clone https://github.com/CXPhoenix/aisp-mission-board.git
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

![Cloudflare](https://img.shields.io/badge/Tunnel_Service-BF6BF2?logo=Cloudflare&logoColor=white&label=Cloudflare&labelColor=F38020)

所有服務皆透過 Cloudflare Tunnel 服務提供存取。

## 專案結構

```
aisp-mission-board/
├── app/
│   ├── main.py              # FastAPI 應用程式進入點
│   ├── configs/             # 組態設定類別
│   ├── migrations/          # Beanie ODM 資料庫遷移檔案
│   ├── migration_cli.py     # 遷移系統 CLI 工具
│   ├── migration_runner.py  # 自動遷移執行器
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
│   │   ├── mall_pages.py   # 商城路由
│   │   └── admin_pages/    # 管理者功能
│   ├── shared/             # 共用工具和中介軟體
│   │   ├── odm.py         # MongoDB 連線管理
│   │   ├── sessions.py    # Session 中介軟體
│   │   ├── dependencies.py # FastAPI 依賴注入
│   │   ├── link_utils.py  # 通用連結工具模組
│   │   └── webpage.py     # 模板渲染工具
│   ├── templates/          # Jinja2 HTML 模板
│   │   ├── admin/         # 管理者介面模板
│   │   │   ├── physical_product_requests.html # 實體商品申請審核
│   │   │   ├── product_form.html # 商品表單
│   │   │   └── product_list.html # 商品列表
│   │   ├── mall/          # 商城介面模板
│   │   │   ├── mall_board.html # 商城首頁
│   │   │   ├── mall_detail.html # 商品詳情頁
│   │   │   └── mall_physical_requests.html # 實體商品申請
│   │   ├── mission/       # 任務介面模板
│   │   └── user/          # 使用者介面模板
│   └── public/            # 靜態資源
├── data/                   # 資料儲存目錄
│   ├── db/                # MongoDB 資料
│   └── logs/              # 應用程式日誌
├── env.d/                 # 環境變數設定檔案
├── MIGRATION_TUTORIAL.md  # 遷移系統教學文件
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

### 資料庫遷移

#### 使用官方 Beanie CLI（推薦）

```bash
# 建立新的遷移檔案
docker-compose exec app uv run beanie new-migration -n <migration_name> -p /app/migrations

# 執行遷移（Forward）
docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations

# 回滾遷移（Backward）
docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations --backward

# 限制遷移距離
docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations --distance 1
```

#### 使用容器 CLI 封裝器

```bash
# 建立新的遷移檔案
docker-compose exec app uv run python -m app.migration_cli new <migration_name>

# 執行所有配置資料庫的遷移
docker-compose exec app uv run python -m app.migration_cli migrate

# 針對特定資料庫執行遷移
docker-compose exec app uv run python -m app.migration_cli migrate --database userdb --distance 1

# 預覽遷移操作
docker-compose exec app uv run python -m app.migration_cli migrate --dry-run

# 檢查遷移狀態
docker-compose exec app uv run python -m app.migration_cli status

# 初始化遷移系統
docker-compose exec app uv run python -m app.migration_cli init
```

#### 遷移開發流程

1. **修改模型**：編輯 `app/models/` 目錄中的 Beanie ODM 模型
2. **建立遷移**：使用 CLI 建立遷移檔案
3. **實作遷移**：編輯生成的遷移檔案，使用 Forward/Backward 類別結構
4. **測試遷移**：在開發環境中測試遷移作業的正確性
5. **部署**：容器重啟時自動執行待處理的遷移

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

## API 文件（目前未開放）

![Concealed](https://img.shields.io/badge/Open_API_Documentation-Concealed-orange.svg)

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

- **虛擬商城系統**
  - 商品瀏覽和詳情頁面
  - 虛擬商品購買功能
  - 實體商品申請與審核流程
  - 使用者物品庫存管理
  - Token 交易系統

- **管理者功能**
  - 任務建立和編輯
  - 使用者管理
  - 任務審核系統
  - 商品管理與上架
  - 實體商品申請審核
  - 統計報表

- **資料庫遷移系統**
  - 官方 Beanie ODM 遷移框架整合
  - Forward/Backward 遷移類別結構
  - 容器化 CLI 工具封裝器
  - 應用程式啟動時自動執行遷移
  - 多資料庫遷移支援（userdb、malldb、recorddb、AiSP-Mission）
  - Iterative 和 Free-fall 遷移模式
  - 遷移狀態追蹤與預覽功能

### 🚧 開發中功能

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

1. **成就系統開發**
   - 成就模型完整實作 (`app/models/badge.py`)
   - 成就解鎖邏輯
   - 成就展示頁面
   - 成就系統與任務系統整合

### 🟡 中優先度

2. **操作紀錄系統**
   - 管理者操作日誌 (`app/models/record.py`)
   - 使用者行為追蹤
   - 系統稽核報表

3. **系統最佳化**
   - 錯誤處理改善
   - 效能優化
   - 生產環境設定清理

### 🟢 低優先度

4. **使用者體驗改善**
   - 介面優化
   - 回應式設計改善
   - 載入效能提升

5. **文件和測試**
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

### v0.6.0 (目前版本)
- 🔄 **實作完整的 Beanie ODM 資料庫遷移系統**
  - 整合官方 Beanie ODM 遷移框架，支援 Forward/Backward 遷移結構
  - 新增容器化 CLI 工具封裝器，方便在 Docker 環境中進行遷移管理
  - 實作 FastAPI 應用程式啟動時自動執行遷移功能
  - 提供多資料庫遷移支援，涵蓋 userdb、malldb、recorddb、AiSP-Mission 等多個資料庫
  - 支援 Iterative 和 Free-fall 兩種遷移模式
  - 新增遷移狀態追蹤、預覽功能與完整的 CLI 命令支援
- 🔐 **新增使用者密碼變更功能**
  - 提供使用者自助密碼變更介面與後端驗證機制
- 📚 **完善遷移系統文件**
  - 新增 MIGRATION_TUTORIAL.md 詳細教學文件
  - 更新 CLAUDE.md 開發指南，包含遷移系統最佳實踐
- 🎨 **優化管理介面與模板**
  - 改善管理者介面的樣式與使用者體驗
  - 更新基礎模板與公共資源

### v0.5.0
- 🛍️ 完整實作虛擬商城系統與實體商品申請功能
- 🔧 新增 MongoDB 服務健康檢查與依賴更新
- 📝 更新專案描述以反映正確的程式名稱
- 📚 新增 Claude Code 開發指南與相關環境設定
- 🎯 完善管理者系統與任務審核流程
- ⚡ 增強 FastAPI 應用程式的自訂錯誤處理和路由
- 🏗️ 優化專案結構與程式碼可讀性

### v0.1.0
- 基礎架構建立
- 使用者管理系統
- 任務管理系統
- 管理者功能初步實作
- Docker 部署設定

## 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 聯絡資訊

如有任何問題或建議，請透過 GitHub Issues 聯繫我們。
