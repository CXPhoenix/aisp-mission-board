"""
Free Fall Migration 範例：重構 Mission 狀態系統
建立時間：2024-12-07 12:00:01

這個 migration 示範如何使用 Beanie 的 free fall migration 系統
進行複雜的資料結構重組和批次處理操作。
"""
from beanie import free_fall_migration
from motor.motor_asyncio import AsyncIOMotorClientSession

# 匯入你的模型類別
from models.mission import Mission, MissionSubmitted


class Forward:
    """向前遷移：重構任務狀態系統"""
    
    @free_fall_migration(document_models=[Mission, MissionSubmitted])
    async def restructure_mission_status(self, session: AsyncIOMotorClientSession):
        """
        執行複雜的任務狀態系統重構
        
        這個範例展示如何：
        1. 更新任務狀態欄位格式
        2. 建立新的關聯文件
        3. 更新文件間的關聯關係
        4. 批次處理大量資料
        
        參數：
            session: MongoDB session，支援事務處理確保資料一致性
        """
        
        # 範例 1：更新所有使用舊狀態格式的任務
        # async for mission in Mission.find_all():
        #     # 將舊的狀態格式轉換為新格式
        #     if hasattr(mission, 'old_status_field'):
        #         mission.new_status = transform_status(mission.old_status_field)
        #         # 移除舊欄位
        #         delattr(mission, 'old_status_field')
        #         await mission.save(session=session)
        
        # 範例 2：為報表功能建立統計文件
        # mission_stats = []
        # async for submission in MissionSubmitted.find_all():
        #     # 建立任務統計資料
        #     stats = {
        #         'mission_id': submission.mission_id,
        #         'submitted_at': submission.submitted_at,
        #         'user_id': submission.user_id,
        #         'completion_time': calculate_completion_time(submission)
        #     }
        #     mission_stats.append(stats)
        
        # 範例 3：批次操作以提升效能
        # if mission_stats:
        #     # 批次插入統計資料
        #     await MissionStats.insert_many(mission_stats, session=session)
        
        # 範例 4：更新使用者的任務關聯
        # async for user in User.find_all():
        #     # 更新使用者的完成任務清單
        #     user.completed_missions_count = len(user.completed_missions)
        #     await user.save(session=session)
        
        # 此範例僅作示範用途
        print("向前遷移：任務狀態系統重構完成")


class Backward:
    """向後遷移（回滾）：還原任務狀態系統"""
    
    @free_fall_migration(document_models=[Mission, MissionSubmitted])
    async def revert_mission_status(self, session: AsyncIOMotorClientSession):
        """
        還原任務狀態系統重構
        
        這個回滾操作應該撤銷在向前遷移中所做的所有變更，
        確保資料能夠安全地回到遷移前的狀態。
        
        參數：
            session: MongoDB session，支援事務處理確保回滾的一致性
        """
        
        # 範例 1：還原狀態格式變更
        # async for mission in Mission.find_all():
        #     if hasattr(mission, 'new_status'):
        #         mission.old_status_field = revert_status(mission.new_status)
        #         delattr(mission, 'new_status')
        #         await mission.save(session=session)
        
        # 範例 2：移除建立的統計文件
        # await MissionStats.delete_all(session=session)
        
        # 範例 3：還原使用者關聯更新
        # async for user in User.find_all():
        #     # 移除新增的計數欄位
        #     if hasattr(user, 'completed_missions_count'):
        #         delattr(user, 'completed_missions_count')
        #         await user.save(session=session)
        
        # 此範例僅作示範用途
        print("向後遷移：任務狀態系統重構已還原")