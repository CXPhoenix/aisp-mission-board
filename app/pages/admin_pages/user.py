from typing import Annotated, Optional
import io
import csv

from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from beanie import PydanticObjectId
from beanie.operators import RegEx, In

# for type hint
from models.user import User
from shared import WebPage
from shared.dependencies import get_admin_role_user
from shared.types import Role

router = APIRouter(prefix="/users", dependencies=[Depends(get_admin_role_user)])


@router.get("/index.html")
@router.get("/")
@WebPage.build().page("admin/user_list.html", "用戶管理")
async def user_list_page(
    request: Request, 
    admin_user: Annotated[User, Depends(get_admin_role_user)],
    search: Optional[str] = None,
    role: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    # 建立查詢條件
    query_conditions = []
    
    if search:
        search_conditions = [
            RegEx(User.campus_id, search, "i"),
            RegEx(User.name, search, "i")
        ]
        query_conditions.append({"$or": search_conditions})
    
    if role and role != "all":
        query_conditions.append(In(User.roles, [Role(role)]))
    
    # 執行查詢
    skip = (page - 1) * limit
    
    if query_conditions:
        users_query = User.find({"$and": query_conditions})
    else:
        users_query = User.find_all()
    
    total_users = await users_query.count()
    users = await users_query.skip(skip).limit(limit).to_list()
    
    # 轉換用戶資料
    users_data = []
    for user in users:
        users_data.append({
            "id": str(user.id),
            "campus_id": user.campus_id,
            "name": user.name,
            "roles": user.roles,
            "level": user.level,
            "token": user.token,
            "disabled": user.disabled,
            "create_time": user.create_time,
            "last_signin_time": user.last_signin_time
        })
    
    # 計算分頁資訊
    total_pages = (total_users + limit - 1) // limit
    
    return {
        "users": users_data,
        "search": search or "",
        "role": role or "all",
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_users": total_users,
            "limit": limit,
            "has_previous": page > 1,
            "has_next": page < total_pages,
            "previous_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page < total_pages else None
        },
        "roles": [{"value": "all", "label": "所有角色"}] + [
            {"value": role.value, "label": role.value} for role in Role
        ]
    }


@router.get("/{user_id}/detail.html")
@WebPage.build().page("admin/user_detail.html", "用戶詳情")
async def user_detail_page(
    request: Request,
    user_id: str,
    admin_user: Annotated[User, Depends(get_admin_role_user)]
):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
    except Exception:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    # 獲取用戶的任務統計
    ongoing_missions_count = len(user.ongoing_missions)
    completed_missions_count = len(user.completed_missions)
    review_pending_count = len(user.review_pending_missions)
    bag_items_count = len(user.bag)
    
    user_data = {
        "id": str(user.id),
        "campus_id": user.campus_id,
        "name": user.name,
        "roles": user.roles,
        "level": user.level,
        "token": user.token,
        "disabled": user.disabled,
        "create_time": user.create_time,
        "last_signin_time": user.last_signin_time,
        "max_missions": user.max_missions,
        "stats": {
            "ongoing_missions": ongoing_missions_count,
            "completed_missions": completed_missions_count,
            "review_pending": review_pending_count,
            "bag_items": bag_items_count
        }
    }
    
    return {"user": user_data}


@router.get("/create.html")
@WebPage.build().page("admin/user_form.html", "新增用戶")
async def user_create_page(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_role_user)]
):
    return {
        "mode": "create",
        "user": None,
        "roles": [{"value": role.value, "label": role.value} for role in Role]
    }


@router.post("/create")
async def user_create_action(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_role_user)],
    campus_id: Annotated[str, Form(...)],
    name: Annotated[str, Form(...)],
    password: Annotated[str, Form(...)],
    roles: Annotated[list[str], Form()] = None,
    level: Annotated[int, Form()] = 1,
    token: Annotated[int, Form()] = 0,
    max_missions: Annotated[int, Form()] = 1,
    disabled: Annotated[bool, Form()] = False
):
    try:
        # 檢查校園ID是否已存在
        existing_user = await User.find_one(User.campus_id == campus_id)
        if existing_user:
            request.session["error"] = "校園ID已存在"
            return RedirectResponse(url="/admin/users/create.html", status_code=302)
        
        # 處理角色
        user_roles = []
        if roles:
            for role_str in roles:
                try:
                    user_roles.append(Role(role_str))
                except ValueError:
                    continue
        
        if not user_roles:
            user_roles = [Role.USER]
        
        # 創建新用戶
        new_user = User(
            campus_id=campus_id,
            name=name,
            password=password,
            roles=user_roles,
            level=max(1, level),
            token=max(0, token),
            max_missions=max(1, min(10, max_missions)),
            disabled=disabled
        )
        
        await new_user.save()
        
        request.session["success"] = f"用戶 {name} 創建成功"
        return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"創建用戶失敗: {str(e)}"
        return RedirectResponse(request.url_for('user_create_page'), status_code=302)


@router.get("/{user_id}/edit.html")
@WebPage.build().page("admin/user_form.html", "編輯用戶")
async def user_edit_page(
    request: Request,
    user_id: str,
    admin_user: Annotated[User, Depends(get_admin_role_user)]
):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
    except Exception:
        raise HTTPException(status_code=404, detail="用戶不存在")
    
    user_data = {
        "id": str(user.id),
        "campus_id": user.campus_id,
        "name": user.name,
        "roles": user.roles,
        "level": user.level,
        "token": user.token,
        "max_missions": user.max_missions,
        "disabled": user.disabled
    }
    
    return {
        "mode": "edit",
        "user": user_data,
        "roles": [{"value": role.value, "label": role.value} for role in Role]
    }


@router.post("/{user_id}/edit")
async def user_edit_action(
    request: Request,
    user_id: str,
    admin_user: Annotated[User, Depends(get_admin_role_user)],
    name: Annotated[str, Form(...)],
    password: Annotated[str, Form()] = None,
    roles: Annotated[list[str], Form()] = None,
    level: Annotated[int, Form()] = 1,
    token: Annotated[int, Form()] = 0,
    max_missions: Annotated[int, Form()] = 1,
    disabled: Annotated[bool, Form()] = False
):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 更新用戶資料
        user.name = name
        user.level = max(1, level)
        user.token = max(0, token)
        user.max_missions = max(1, min(10, max_missions))
        user.disabled = disabled
        
        # 更新密碼（如果提供）
        if password and password.strip():
            user.password = password
        
        # 處理角色
        if roles:
            user_roles = []
            for role_str in roles:
                try:
                    user_roles.append(Role(role_str))
                except ValueError:
                    continue
            
            if user_roles:
                user.roles = user_roles
        
        await user.save()
        
        request.session["success"] = f"用戶 {user.name} 更新成功"
        return RedirectResponse(request.url_for('user_detail_page', user_id=user_id), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"更新用戶失敗: {str(e)}"
        return RedirectResponse(request.url_for('user_edit_page', user_id=user_id), status_code=302)


@router.post("/{user_id}/delete")
async def user_delete_action(
    request: Request,
    user_id: str,
    admin_user: Annotated[User, Depends(get_admin_role_user)]
):
    try:
        user = await User.get(PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="用戶不存在")
        
        # 防止刪除自己
        if str(user.id) == str(admin_user.id):
            request.session["error"] = "無法刪除自己的帳戶"
            return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
        # 檢查是否有進行中的任務
        if user.ongoing_missions:
            request.session["error"] = f"用戶 {user.name} 還有進行中的任務，無法刪除"
            return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
        user_name = user.name
        await user.delete()
        
        request.session["success"] = f"用戶 {user_name} 已刪除"
        return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"刪除用戶失敗: {str(e)}"
        return RedirectResponse(request.url_for('user_list_page'), status_code=302)


@router.get("/import.html")
@WebPage.build().page("admin/user_import.html", "批次匯入用戶")
async def user_import_page(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_role_user)]
):
    return {
        "roles": [{"value": role.value, "label": role.value} for role in Role]
    }


@router.post("/import")
async def user_import_action(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_role_user)],
    csv_file: Annotated[UploadFile, File(...)],
    default_role: Annotated[str, Form()] = "user",
    skip_existing: Annotated[bool, Form()] = True
):
    try:
        # 驗證檔案類型
        if not csv_file.filename.endswith('.csv'):
            request.session["error"] = "請上傳CSV檔案"
            return RedirectResponse(request.url_for('user_import_page'), status_code=302)
        
        # 讀取檔案內容
        content = await csv_file.read()
        content_str = content.decode('utf-8-sig')  # 支援BOM
        
        # 解析CSV
        csv_reader = csv.DictReader(io.StringIO(content_str))
        
        # 驗證必要欄位
        required_fields = ['campus_id', 'name', 'password']
        if not all(field in csv_reader.fieldnames for field in required_fields):
            request.session["error"] = f"CSV檔案必須包含以下欄位: {', '.join(required_fields)}"
            return RedirectResponse(request.url_for('user_import_page'), status_code=302)
        
        success_count = 0
        skip_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # 從第2行開始（第1行是標題）
            try:
                campus_id = row['campus_id'].strip()
                name = row['name'].strip()
                password = row['password'].strip()
                
                if not campus_id or not name or not password:
                    errors.append(f"第{row_num}行: 必填欄位不能為空")
                    error_count += 1
                    continue
                
                # 檢查是否已存在
                existing_user = await User.find_one(User.campus_id == campus_id)
                if existing_user:
                    if skip_existing:
                        skip_count += 1
                        continue
                    else:
                        errors.append(f"第{row_num}行: 校園ID {campus_id} 已存在")
                        error_count += 1
                        continue
                
                # 處理角色
                roles_str = row.get('roles', default_role).strip()
                user_roles = []
                if roles_str:
                    for role_str in roles_str.split(','):
                        role_str = role_str.strip()
                        try:
                            user_roles.append(Role(role_str))
                        except ValueError:
                            pass
                
                if not user_roles:
                    user_roles = [Role(default_role)]
                
                # 處理其他欄位
                level = int(row.get('level', 1)) if row.get('level', '').strip() else 1
                token = int(row.get('token', 0)) if row.get('token', '').strip() else 0
                max_missions = int(row.get('max_missions', 1)) if row.get('max_missions', '').strip() else 1
                disabled = row.get('disabled', '').strip().lower() in ['true', '1', 'yes', 'on']
                
                # 創建用戶
                new_user = User(
                    campus_id=campus_id,
                    name=name,
                    password=password,
                    roles=user_roles,
                    level=max(1, level),
                    token=max(0, token),
                    max_missions=max(1, min(10, max_missions)),
                    disabled=disabled
                )
                
                await new_user.save()
                success_count += 1
                
            except Exception as e:
                errors.append(f"第{row_num}行: {str(e)}")
                error_count += 1
        
        # 準備結果訊息
        result_msg = f"匯入完成 - 成功: {success_count}, 跳過: {skip_count}, 錯誤: {error_count}"
        
        if errors and len(errors) <= 10:  # 只顯示前10個錯誤
            result_msg += "\n錯誤詳情:\n" + "\n".join(errors[:10])
        elif errors:
            result_msg += "\n錯誤詳情:\n" + "\n".join(errors[:10]) + f"\n... 還有 {len(errors) - 10} 個錯誤"
        
        if success_count > 0:
            request.session["success"] = result_msg
        else:
            request.session["error"] = result_msg
        
        return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"匯入失敗: {str(e)}"
        return RedirectResponse(request.url_for('user_import_page'), status_code=302)


@router.post("/bulk-delete")
async def bulk_delete_users(
    request: Request,
    admin_user: Annotated[User, Depends(get_admin_role_user)],
    user_ids: Annotated[list[str], Form()]
):
    try:
        if not user_ids:
            request.session["error"] = "請選擇要刪除的用戶"
            return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
        deleted_count = 0
        skip_count = 0
        errors = []
        
        for user_id in user_ids:
            try:
                user = await User.get(PydanticObjectId(user_id))
                if not user:
                    continue
                
                # 防止刪除自己
                if str(user.id) == str(admin_user.id):
                    errors.append(f"跳過自己的帳戶: {user.name}")
                    skip_count += 1
                    continue
                
                # 檢查是否有進行中的任務
                if user.ongoing_missions:
                    errors.append(f"跳過 {user.name}: 還有進行中的任務")
                    skip_count += 1
                    continue
                
                await user.delete()
                deleted_count += 1
                
            except Exception as e:
                errors.append(f"刪除用戶失敗: {str(e)}")
                skip_count += 1
        
        # 準備結果訊息
        result_msg = f"批次刪除完成 - 成功: {deleted_count}, 跳過: {skip_count}"
        
        if errors and len(errors) <= 5:  # 只顯示前5個錯誤
            result_msg += "\\n錯誤詳情:\\n" + "\\n".join(errors[:5])
        elif errors:
            result_msg += "\\n錯誤詳情:\\n" + "\\n".join(errors[:5]) + f"\\n... 還有 {len(errors) - 5} 個錯誤"
        
        if deleted_count > 0:
            request.session["success"] = result_msg
        else:
            request.session["error"] = result_msg
        
        return RedirectResponse(request.url_for('user_list_page'), status_code=302)
        
    except Exception as e:
        request.session["error"] = f"批次刪除失敗: {str(e)}"
        return RedirectResponse(request.url_for('user_list_page'), status_code=302)


