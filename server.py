import httpx
import os
import json
from mcp.server.fastmcp import FastMCP

BITRIX_WEBHOOK = os.environ.get("BITRIX_WEBHOOK", "").rstrip("/")

mcp = FastMCP("Bitrix24")

async def b24(method: str, params: dict = {}) -> dict:
    url = f"{BITRIX_WEBHOOK}/{method}.json"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, json=params)
        r.raise_for_status()
        return r.json()

# ─── CRM: Лиды ────────────────────────────────────────────────────────────────

@mcp.tool()
async def crm_get_leads(limit: int = 20, filter: str = "") -> str:
    """Получить список лидов из CRM. filter — JSON строка фильтра, например '{\"STATUS_ID\": \"NEW\"}'"""
    params = {"order": {"DATE_CREATE": "DESC"}, "select": ["ID", "TITLE", "NAME", "LAST_NAME", "PHONE", "EMAIL", "STATUS_ID", "DATE_CREATE", "ASSIGNED_BY_ID"], "start": 0}
    params["limit"] = limit
    if filter:
        try:
            params["filter"] = json.loads(filter)
        except Exception:
            pass
    result = await b24("crm.lead.list", params)
    leads = result.get("result", [])
    return json.dumps(leads, ensure_ascii=False, indent=2)

@mcp.tool()
async def crm_get_lead(lead_id: int) -> str:
    """Получить детали конкретного лида по ID"""
    result = await b24("crm.lead.get", {"id": lead_id})
    return json.dumps(result.get("result", {}), ensure_ascii=False, indent=2)

@mcp.tool()
async def crm_create_lead(title: str, name: str = "", last_name: str = "", phone: str = "", email: str = "", comments: str = "") -> str:
    """Создать новый лид в CRM"""
    fields = {"TITLE": title}
    if name: fields["NAME"] = name
    if last_name: fields["LAST_NAME"] = last_name
    if phone: fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
    if email: fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]
    if comments: fields["COMMENTS"] = comments
    result = await b24("crm.lead.add", {"fields": fields})
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def crm_update_lead(lead_id: int, fields: str) -> str:
    """Обновить лид. fields — JSON строка с полями, например '{\"STATUS_ID\": \"IN_PROCESS\"}'"""
    result = await b24("crm.lead.update", {"id": lead_id, "fields": json.loads(fields)})
    return json.dumps(result, ensure_ascii=False)

# ─── CRM: Сделки ──────────────────────────────────────────────────────────────

@mcp.tool()
async def crm_get_deals(limit: int = 20, filter: str = "") -> str:
    """Получить список сделок из CRM"""
    params = {"order": {"DATE_CREATE": "DESC"}, "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "CURRENCY_ID", "CONTACT_ID", "COMPANY_ID", "ASSIGNED_BY_ID", "DATE_CREATE"], "start": 0, "limit": limit}
    if filter:
        try:
            params["filter"] = json.loads(filter)
        except Exception:
            pass
    result = await b24("crm.deal.list", params)
    return json.dumps(result.get("result", []), ensure_ascii=False, indent=2)

@mcp.tool()
async def crm_get_deal(deal_id: int) -> str:
    """Получить детали сделки по ID"""
    result = await b24("crm.deal.get", {"id": deal_id})
    return json.dumps(result.get("result", {}), ensure_ascii=False, indent=2)

@mcp.tool()
async def crm_create_deal(title: str, stage_id: str = "NEW", opportunity: float = 0, contact_id: int = 0) -> str:
    """Создать новую сделку"""
    fields = {"TITLE": title, "STAGE_ID": stage_id}
    if opportunity: fields["OPPORTUNITY"] = opportunity
    if contact_id: fields["CONTACT_ID"] = contact_id
    result = await b24("crm.deal.add", {"fields": fields})
    return json.dumps(result, ensure_ascii=False)

# ─── CRM: Контакты ────────────────────────────────────────────────────────────

@mcp.tool()
async def crm_get_contacts(limit: int = 20, filter: str = "") -> str:
    """Получить список контактов"""
    params = {"order": {"DATE_CREATE": "DESC"}, "select": ["ID", "NAME", "LAST_NAME", "PHONE", "EMAIL", "COMPANY_ID"], "start": 0, "limit": limit}
    if filter:
        try:
            params["filter"] = json.loads(filter)
        except Exception:
            pass
    result = await b24("crm.contact.list", params)
    return json.dumps(result.get("result", []), ensure_ascii=False, indent=2)

@mcp.tool()
async def crm_create_contact(name: str, last_name: str = "", phone: str = "", email: str = "") -> str:
    """Создать контакт в CRM"""
    fields = {"NAME": name}
    if last_name: fields["LAST_NAME"] = last_name
    if phone: fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
    if email: fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]
    result = await b24("crm.contact.add", {"fields": fields})
    return json.dumps(result, ensure_ascii=False)

# ─── Задачи ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def tasks_get(limit: int = 20, filter: str = "") -> str:
    """Получить список задач. filter — JSON строка, например '{\"STATUS\": \"2\"}' (2=в работе, 3=завершена)"""
    params = {"order": {"CREATED_DATE": "desc"}, "select": ["ID", "TITLE", "STATUS", "RESPONSIBLE_ID", "CREATED_DATE", "DEADLINE", "DESCRIPTION"], "params": {"NAV_PARAMS": {"nPageSize": limit}}}
    if filter:
        try:
            params["filter"] = json.loads(filter)
        except Exception:
            pass
    result = await b24("tasks.task.list", params)
    tasks = result.get("result", {}).get("tasks", [])
    return json.dumps(tasks, ensure_ascii=False, indent=2)

@mcp.tool()
async def tasks_get_task(task_id: int) -> str:
    """Получить детали задачи по ID"""
    result = await b24("tasks.task.get", {"taskId": task_id, "select": ["ID", "TITLE", "DESCRIPTION", "STATUS", "RESPONSIBLE_ID", "CREATED_DATE", "DEADLINE", "TAGS", "COMMENTS_COUNT"]})
    return json.dumps(result.get("result", {}).get("task", {}), ensure_ascii=False, indent=2)

@mcp.tool()
async def tasks_create(title: str, description: str = "", responsible_id: int = 0, deadline: str = "") -> str:
    """Создать задачу. deadline формат: 2026-06-30T18:00:00"""
    fields = {"TITLE": title}
    if description: fields["DESCRIPTION"] = description
    if responsible_id: fields["RESPONSIBLE_ID"] = responsible_id
    if deadline: fields["DEADLINE"] = deadline
    result = await b24("tasks.task.add", {"fields": fields})
    return json.dumps(result.get("result", {}), ensure_ascii=False)

@mcp.tool()
async def tasks_update(task_id: int, fields: str) -> str:
    """Обновить задачу. fields — JSON строка с полями"""
    result = await b24("tasks.task.update", {"taskId": task_id, "fields": json.loads(fields)})
    return json.dumps(result.get("result", {}), ensure_ascii=False)

@mcp.tool()
async def tasks_complete(task_id: int) -> str:
    """Завершить задачу"""
    result = await b24("tasks.task.complete", {"taskId": task_id})
    return json.dumps(result, ensure_ascii=False)

# ─── Телефония / звонки ───────────────────────────────────────────────────────

@mcp.tool()
async def telephony_get_calls(limit: int = 20, filter: str = "") -> str:
    """Получить список звонков. filter — JSON строка, например '{\"CALL_TYPE\": \"1\"}' (1=вход, 2=исход)"""
    params = {"order": {"CALL_START_DATE": "DESC"}, "select": ["ID", "CALL_TYPE", "CALL_DURATION", "CALL_START_DATE", "PHONE_NUMBER", "PORTAL_USER_ID", "CRM_ENTITY_TYPE", "CRM_ENTITY_ID", "CALL_FAILED_CODE"], "filter": {}, "limit": limit}
    if filter:
        try:
            params["filter"].update(json.loads(filter))
        except Exception:
            pass
    result = await b24("voximplant.statistic.get", params)
    return json.dumps(result.get("result", []), ensure_ascii=False, indent=2)

@mcp.tool()
async def telephony_get_stats(date_from: str = "", date_to: str = "") -> str:
    """Получить статистику звонков за период. Формат дат: 2026-05-01"""
    filter_params = {}
    if date_from: filter_params[">CALL_START_DATE"] = date_from
    if date_to: filter_params["<CALL_START_DATE"] = date_to
    result = await b24("voximplant.statistic.get", {"filter": filter_params, "select": ["PORTAL_USER_ID", "CALL_TYPE", "CALL_DURATION", "CALL_FAILED_CODE"], "limit": 50})
    return json.dumps(result.get("result", []), ensure_ascii=False, indent=2)

# ─── Пользователи / сотрудники ────────────────────────────────────────────────

@mcp.tool()
async def users_get(limit: int = 50, active_only: bool = True) -> str:
    """Получить список сотрудников"""
    params = {"select": ["ID", "NAME", "LAST_NAME", "EMAIL", "PERSONAL_PHONE", "WORK_PHONE", "UF_DEPARTMENT", "ACTIVE"], "filter": {}}
    if active_only:
        params["filter"]["ACTIVE"] = True
    result = await b24("user.get", params)
    return json.dumps(result.get("result", []), ensure_ascii=False, indent=2)

@mcp.tool()
async def users_get_user(user_id: int) -> str:
    """Получить информацию о сотруднике по ID"""
    result = await b24("user.get", {"filter": {"ID": user_id}})
    users = result.get("result", [])
    return json.dumps(users[0] if users else {}, ensure_ascii=False, indent=2)

@mcp.tool()
async def users_get_current() -> str:
    """Получить информацию о текущем пользователе вебхука"""
    result = await b24("profile")
    return json.dumps(result.get("result", {}), ensure_ascii=False, indent=2)

# ─── Запуск ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    transport = sys.argv[1] if len(sys.argv) > 1 else "sse"
    if transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")
