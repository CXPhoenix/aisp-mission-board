"""
Iterative Migration 範例：為 User 模型新增 last_login 欄位
建立時間：2024-12-07 12:00:00

這個 migration 示範如何使用 Beanie 的 iterative migration 系統
為現有模型新增欄位的完整流程。
"""
from beanie import iterative_migration
from datetime import datetime
from typing import Optional

# 匯入你的模型類別 - 這些應該是實際的模型類別
# 在這個範例中，我們使用簡化的模型定義來示範
from models.user import User


class OldUser:
    """代表 migration 前的 User 模型結構"""
    # 這裡應該包含舊的欄位結構
    # 在實際應用中，你會在這裡定義 migration 前的模型狀態
    pass


class Forward:
    """向前遷移：為 User 模型新增 last_login 欄位"""
    
    @iterative_migration()
    async def add_last_login_field(
        self, input_document: OldUser, output_document: User
    ):
        """
        為現有的 User 文件新增 last_login 欄位
        
        參數：
            input_document: migration 前的 User 文件
            output_document: migration 後的 User 文件
        """
        # 將所有現有欄位從輸入文件複製到輸出文件
        # 在實際的 migration 中，你需要複製所有實際的欄位
        # 範例：
        # output_document.campus_id = input_document.campus_id
        # output_document.name = input_document.name
        # output_document.password = input_document.password
        # output_document.roles = input_document.roles
        # ... (其他現有欄位)
        
        # 新增 last_login 欄位
        # output_document.last_login = None  # 為現有使用者設定預設值
        
        # 此範例僅作示範用途，實際實作時需要處理真實的欄位複製
        pass


class Backward:
    """向後遷移（回滾）：從 User 模型移除 last_login 欄位"""
    
    @iterative_migration()
    async def remove_last_login_field(
        self, input_document: User, output_document: OldUser
    ):
        """
        從 User 文件中移除 last_login 欄位
        
        參數：
            input_document: migration 後的 User 文件
            output_document: migration 前的 User 文件（回滾目標）
        """
        # 複製除了 last_login 以外的所有欄位
        # 這樣就能有效地移除 last_login 欄位
        # 範例：
        # output_document.campus_id = input_document.campus_id
        # output_document.name = input_document.name
        # output_document.password = input_document.password
        # output_document.roles = input_document.roles
        # ... (其他需要保留的欄位，但不包含 last_login)
        
        # 此範例僅作示範用途，實際實作時需要處理真實的欄位複製
        pass