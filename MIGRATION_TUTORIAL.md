# Beanie ODM Migration 教學指南

## 📋 目錄

1. [基本概念](#基本概念)
2. [Migration 類型](#migration-類型)
3. [CLI 指令使用](#cli-指令使用)
4. [多資料庫架構](#多資料庫架構)
5. [最佳實踐](#最佳實踐)
6. [實際範例](#實際範例)
7. [故障排除](#故障排除)

## 基本概念

### 什麼是資料庫 Migration？

資料庫 Migration 是一種版本控制機制，用於管理資料庫 Schema 和資料的演進變化。當你的應用程式 Model 發生變更時，Migration 可以安全地將現有資料轉換為新的結構。

### 為什麼需要 Migration？

- **版本控制**：追蹤資料庫 Schema 的變更歷史
- **團隊協作**：確保所有開發者和環境的資料庫狀態一致
- **安全部署**：提供可控的資料庫更新機制
- **Rollback 支援**：在出現問題時能夠安全地還原變更

### Beanie ODM Migration 系統

Beanie ODM 提供了一套完整的 Migration 系統，支援：
- **Forward Migration**：應用新的變更
- **Backward Migration**：Rollback 到之前的版本
- **Transaction 支援**：確保資料一致性
- **Batch Processing**：高效處理大量資料

## Migration 類型

### 1. Iterative Migration

**推薦用於 99% 的情況**

特點：
- 使用 `@iterative_migration()` Decorator
- 逐一處理 Document
- 簡單易懂的語法
- 適用於欄位新增、修改、刪除等常見操作

基本結構：
```python
from beanie import iterative_migration

class Forward:
    @iterative_migration()
    async def migration_method(self, input_document: OldModel, output_document: NewModel):
        # Migration 邏輯
        output_document.new_field = input_document.old_field

class Backward:
    @iterative_migration()
    async def rollback_method(self, input_document: NewModel, output_document: OldModel):
        # Rollback 邏輯
        output_document.old_field = input_document.new_field
```

### 2. Free Fall Migration

**適用於複雜的資料重組**

特點：
- 使用 `@free_fall_migration()` Decorator
- 需要明確指定 Document Model
- 支援 MongoDB Session 進行 Transaction 處理
- 適用於複雜的 Batch 操作和跨 Collection 操作

基本結構：
```python
from beanie import free_fall_migration
from motor.motor_asyncio import AsyncIOMotorClientSession

class Forward:
    @free_fall_migration(document_models=[Model1, Model2])
    async def migration_method(self, session: AsyncIOMotorClientSession):
        # 複雜的 Migration 邏輯
        async for document in Model1.find_all():
            # 處理邏輯
            await document.save(session=session)

class Backward:
    @free_fall_migration(document_models=[Model1, Model2])
    async def rollback_method(self, session: AsyncIOMotorClientSession):
        # Rollback 邏輯
        pass
```

## CLI 指令使用

### 建立新的 Migration

```bash
# 使用官方 Beanie CLI（推薦）
docker-compose exec app uv run beanie new-migration -n <migration_name> -p /app/migrations

# 使用容器 CLI 包裝器
docker-compose exec app uv run python -m app.migration_cli new <migration_name>
```

### 執行 Migration

```bash
# Forward Migration（應用變更）
docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations

# Backward Migration（Rollback 變更）
docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations --backward

# 限制 Migration 距離
docker-compose exec app uv run beanie migrate -uri mongodb://user:pass@mongo:27017 -db <database_name> -p /app/migrations --distance 1
```

### 使用容器 CLI 包裝器

```bash
# 執行所有配置資料庫的 Migration
docker-compose exec app uv run python -m app.migration_cli migrate

# 針對特定資料庫執行 Migration
docker-compose exec app uv run python -m app.migration_cli migrate --database userdb --distance 1

# Dry Run（僅顯示將要執行的操作）
docker-compose exec app uv run python -m app.migration_cli migrate --dry-run

# 檢查 Migration 狀態
docker-compose exec app uv run python -m app.migration_cli status

# 初始化 Migration 系統
docker-compose exec app uv run python -m app.migration_cli init
```

## 多資料庫架構

本專案使用多個 MongoDB 資料庫，每個資料庫服務不同的領域：

### 資料庫分類

- **userdb**：使用者資料 (User Model)
- **malldb**：商城資料 (Product Model)
- **recorddb**：交易紀錄 (TransactionRecord Model)
- **AiSP-Mission**：任務資料 (Mission, MissionSubmitted Model)
- **App-Config**：應用程式配置

### 多資料庫 Migration 策略

1. **分別管理**：每個資料庫的 Migration 檔案分別建立和執行
2. **統一命名**：使用時間戳記加描述的命名方式 `YYYYMMDD_HHMMSS_description.py`
3. **跨資料庫關聯**：使用 Beanie 的 Link/BackLink 管理跨資料庫關聯
4. **Batch 執行**：使用容器 CLI 包裝器一次對所有資料庫執行 Migration

### Migration 檔案組織

```
app/migrations/
├── 20241207_120000_user_add_last_login.py      # userdb Migration
├── 20241207_120001_mission_restructure.py     # AiSP-Mission Migration
├── 20241207_120002_product_add_inventory.py   # malldb Migration
└── 20241207_120003_config_update_schema.py    # App-Config Migration
```

## 最佳實踐

### 1. Migration 檔案命名

```
YYYYMMDD_HHMMSS_descriptive_name.py
```

範例：
- `20241207_120000_user_add_last_login.py`
- `20241207_120001_mission_restructure_status.py`
- `20241207_120002_product_add_inventory_field.py`

### 2. Migration 開發流程

1. **修改 Model**：編輯 `app/models/` 中的 Beanie ODM Model
2. **建立 Migration**：使用 CLI 建立 Migration 檔案
3. **實作 Migration**：編輯生成的 Migration 檔案
4. **測試 Migration**：在開發環境中測試 Migration 的正確性
5. **部署**：容器重啟時自動執行待處理的 Migration

### 3. 安全考量

- **備份資料**：執行 Migration 前務必備份資料庫
- **測試環境**：先在測試環境驗證 Migration
- **Rollback 計劃**：確保每個 Migration 都有對應的 Rollback 邏輯
- **Transaction 支援**：使用 Transaction 確保資料一致性

### 4. 效能最佳化

- **Batch Processing**：使用 `insert_many()` 和 `update_many()` 進行 Batch 操作
- **Index 管理**：在 Migration 後重建必要的 Index
- **Memory 管理**：處理大量資料時注意 Memory 使用

### 5. 程式碼品質

- **詳細註解**：使用中文註解說明 Migration 目的和邏輯
- **Error Handling**：適當的 Exception 處理和 Log 記錄
- **測試覆蓋**：雖然沒有自動化測試框架，但要手動測試所有情況

## 實際範例

### 範例 1：為 User Model 新增欄位

```python
"""
為 User Model 新增 last_login 欄位
建立時間：2024-12-07 12:00:00
"""
from beanie import iterative_migration
from datetime import datetime
from typing import Optional
from app.models.user import User

class OldUser:
    """Migration 前的 User Model 結構"""
    campus_id: str
    name: str
    password: str
    roles: list

class Forward:
    @iterative_migration()
    async def add_last_login_field(self, input_document: OldUser, output_document: User):
        """為現有的 User Document 新增 last_login 欄位"""
        # 複製現有欄位
        output_document.campus_id = input_document.campus_id
        output_document.name = input_document.name
        output_document.password = input_document.password
        output_document.roles = input_document.roles
        
        # 新增欄位
        output_document.last_login = None  # 設定預設值

class Backward:
    @iterative_migration()
    async def remove_last_login_field(self, input_document: User, output_document: OldUser):
        """移除 last_login 欄位"""
        # 只複製原有欄位，不包含 last_login
        output_document.campus_id = input_document.campus_id
        output_document.name = input_document.name
        output_document.password = input_document.password
        output_document.roles = input_document.roles
```

### 範例 2：商品庫存系統重構

```python
"""
重構商品庫存系統
建立時間：2024-12-07 12:00:01
"""
from beanie import free_fall_migration
from motor.motor_asyncio import AsyncIOMotorClientSession
from app.models.product import Product

class Forward:
    @free_fall_migration(document_models=[Product])
    async def restructure_inventory_system(self, session: AsyncIOMotorClientSession):
        """重構商品庫存系統"""
        
        # 批次更新所有商品的庫存資訊
        async for product in Product.find_all():
            # 將舊的庫存格式轉換為新格式
            if hasattr(product, 'old_stock'):
                product.inventory = {
                    'available': product.old_stock,
                    'reserved': 0,
                    'total': product.old_stock
                }
                # 移除舊欄位
                delattr(product, 'old_stock')
                await product.save(session=session)

class Backward:
    @free_fall_migration(document_models=[Product])
    async def revert_inventory_system(self, session: AsyncIOMotorClientSession):
        """還原庫存系統"""
        
        async for product in Product.find_all():
            if hasattr(product, 'inventory'):
                # 還原為舊格式
                product.old_stock = product.inventory['available']
                delattr(product, 'inventory')
                await product.save(session=session)
```

### 範例 3：任務狀態標準化

```python
"""
標準化任務狀態系統
建立時間：2024-12-07 12:00:02
"""
from beanie import iterative_migration
from app.models.mission import Mission

class OldMission:
    """Migration 前的 Mission Model"""
    status: str  # 舊的 Status 格式：'active', 'inactive', 'completed'

class Forward:
    @iterative_migration()
    async def standardize_mission_status(self, input_document: OldMission, output_document: Mission):
        """標準化 Mission Status"""
        # 複製其他欄位
        output_document.title = input_document.title
        output_document.description = input_document.description
        output_document.points = input_document.points
        
        # 轉換 Status 格式
        status_mapping = {
            'active': 'ACTIVE',
            'inactive': 'INACTIVE', 
            'completed': 'COMPLETED'
        }
        output_document.status = status_mapping.get(input_document.status, 'ACTIVE')

class Backward:
    @iterative_migration()
    async def revert_mission_status(self, input_document: Mission, output_document: OldMission):
        """還原 Mission Status 格式"""
        # 複製其他欄位
        output_document.title = input_document.title
        output_document.description = input_document.description
        output_document.points = input_document.points
        
        # 還原 Status 格式
        status_mapping = {
            'ACTIVE': 'active',
            'INACTIVE': 'inactive',
            'COMPLETED': 'completed'
        }
        output_document.status = status_mapping.get(input_document.status, 'active')
```

## 故障排除

### 常見問題與解決方案

#### 1. Migration 執行失敗

**問題**：Migration 在執行過程中發生錯誤

**解決方案**：
- 檢查資料庫 Connection String 是否正確
- 確認資料庫有足夠的權限
- 檢查 Migration 檔案的語法錯誤
- 使用 `--dry-run` 選項先測試 Migration

#### 2. Transaction 支援問題

**問題**：`MongoError: This MongoDB deployment does not support retryable writes`

**解決方案**：
- 確保 MongoDB 以 Replica Set 模式運行
- 或者使用 `--no-use-transaction` 選項禁用 Transaction

#### 3. Memory 不足

**問題**：處理大量資料時 Memory 不足

**解決方案**：
- 使用 Batch Processing 減少 Memory 使用
- 增加容器的 Memory 限制
- 分段處理大型 Collection

#### 4. Migration 版本衝突

**問題**：多個開發者同時建立 Migration 導致版本衝突

**解決方案**：
- 使用精確的 Timestamp 命名
- 建立 Migration 前先同步最新的程式碼
- 必要時重命名 Migration 檔案

#### 5. 資料類型轉換錯誤

**問題**：欄位類型變更導致的轉換錯誤

**解決方案**：
- 在 Migration 中加入適當的類型檢查
- 提供預設值處理機制
- 使用 try-catch 處理 Exception 情況

### Debug 技巧

#### 1. 使用 Logging

```python
import logging

class Forward:
    @iterative_migration()
    async def migration_method(self, input_document, output_document):
        try:
            # Migration 邏輯
            logging.info(f"Processing document: {input_document.id}")
        except Exception as e:
            logging.error(f"Migration failed for document {input_document.id}: {e}")
            raise
```

#### 2. Dry Run 測試

```bash
# 先執行 Dry Run 查看將要進行的操作
docker-compose exec app uv run python -m app.migration_cli migrate --dry-run
```

#### 3. 分階段測試

```python
# 在 Migration 中加入 Checkpoint
class Forward:
    @iterative_migration()
    async def migration_method(self, input_document, output_document):
        # Checkpoint 1：資料驗證
        if not input_document.required_field:
            raise ValueError("Missing required field")
        
        # Checkpoint 2：轉換邏輯
        output_document.new_field = transform_data(input_document.old_field)
        
        # Checkpoint 3：結果驗證
        if not output_document.new_field:
            raise ValueError("Transformation failed")
```

## 進階主題

### 1. 自動化 Migration

本專案在容器啟動時自動執行待處理的 Migration：

```python
# app/migration_runner.py
async def run_migrations():
    """自動執行待處理的 Migration"""
    # 檢查並執行 Migration
    # 在 main.py 的 lifespan 中調用
```

### 2. Migration 監控

```python
# 在 Migration 中加入監控
class Forward:
    @iterative_migration()
    async def migration_method(self, input_document, output_document):
        # 記錄 Migration 進度
        migration_progress.increment()
        
        # Migration 邏輯
        # ...
        
        # 記錄完成
        migration_progress.complete()
```

### 3. 條件式 Migration

```python
# 根據條件決定是否執行 Migration
class Forward:
    @iterative_migration()
    async def conditional_migration(self, input_document, output_document):
        # 只對符合條件的 Document 執行 Migration
        if input_document.version < 2:
            output_document.new_field = "default_value"
            output_document.version = 2
```

---

## 📚 相關資源

- [Beanie ODM 官方文件](https://beanie-odm.dev/)
- [MongoDB 官方文件](https://docs.mongodb.com/)
- [FastAPI 官方文件](https://fastapi.tiangolo.com/)
- [Docker Compose 官方文件](https://docs.docker.com/compose/)

---

**注意**：本教學基於 Beanie ODM 的最新版本編寫，請確保你使用的版本與教學中的範例相容。在執行任何遷移之前，請務必備份你的資料庫。