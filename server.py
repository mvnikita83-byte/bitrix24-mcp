import httpx
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio

BITRIX_WEBHOOK = os.environ.get("BITRIX_WEBHOOK", "").rstrip("/")

app = FastAPI()

async def b24(method: str, params: dict = {}) -> dict:
    url = f"{BITRIX_WEBHOOK}/{method}.json"
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(url, json=params)
        r.raise_for_status()
        return r.json()

TOOLS = [

    # ───────────── ЛИДЫ ─────────────
    {
        "name": "crm_get_leads",
        "description": "Получить список лидов из CRM Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество лидов", "default": 20},
                "status_id": {"type": "string", "description": "Фильтр по стадии (например: NEW, IN_PROCESS)"}
            }
        }
    },
    {
        "name": "crm_get_lead",
        "description": "Получить один лид по ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID лида"}
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "crm_create_lead",
        "description": "Создать новый лид в CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Название лида"},
                "name": {"type": "string", "description": "Имя"},
                "last_name": {"type": "string", "description": "Фамилия"},
                "phone": {"type": "string", "description": "Телефон"},
                "email": {"type": "string", "description": "Email"},
                "status_id": {"type": "string", "description": "Стадия лида"},
                "assigned_by_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "comment": {"type": "string", "description": "Комментарий"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "crm_update_lead",
        "description": "Обновить лид: сменить стадию, ответственного, имя, телефон и другие поля",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID лида"},
                "title": {"type": "string", "description": "Новое название"},
                "name": {"type": "string", "description": "Имя"},
                "last_name": {"type": "string", "description": "Фамилия"},
                "phone": {"type": "string", "description": "Телефон"},
                "email": {"type": "string", "description": "Email"},
                "status_id": {"type": "string", "description": "Стадия лида (NEW, IN_PROCESS, CONVERTED, JUNK и др.)"},
                "assigned_by_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "comment": {"type": "string", "description": "Комментарий"}
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "crm_delete_lead",
        "description": "Удалить лид по ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer", "description": "ID лида"}
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "crm_get_lead_statuses",
        "description": "Получить список доступных стадий лидов",
        "inputSchema": {"type": "object", "properties": {}}
    },

    # ───────────── СДЕЛКИ ─────────────
    {
        "name": "crm_get_deals",
        "description": "Получить список сделок из CRM Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество сделок", "default": 20},
                "stage_id": {"type": "string", "description": "Фильтр по стадии сделки"}
            }
        }
    },
    {
        "name": "crm_get_deal",
        "description": "Получить одну сделку по ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "integer", "description": "ID сделки"}
            },
            "required": ["deal_id"]
        }
    },
    {
        "name": "crm_create_deal",
        "description": "Создать новую сделку в CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Название сделки"},
                "stage_id": {"type": "string", "description": "Стадия сделки"},
                "opportunity": {"type": "number", "description": "Сумма сделки"},
                "assigned_by_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "contact_id": {"type": "integer", "description": "ID контакта"},
                "company_id": {"type": "integer", "description": "ID компании"},
                "comment": {"type": "string", "description": "Комментарий"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "crm_update_deal",
        "description": "Обновить сделку: сменить стадию, ответственного, сумму и другие поля",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "integer", "description": "ID сделки"},
                "title": {"type": "string", "description": "Новое название"},
                "stage_id": {"type": "string", "description": "Стадия сделки"},
                "opportunity": {"type": "number", "description": "Сумма сделки"},
                "assigned_by_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "comment": {"type": "string", "description": "Комментарий"}
            },
            "required": ["deal_id"]
        }
    },
    {
        "name": "crm_delete_deal",
        "description": "Удалить сделку по ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "integer", "description": "ID сделки"}
            },
            "required": ["deal_id"]
        }
    },

    # ───────────── ЗАДАЧИ ─────────────
    {
        "name": "tasks_get",
        "description": "Получить список задач из Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество задач", "default": 20},
                "responsible_id": {"type": "integer", "description": "Фильтр по ответственному (ID сотрудника)"},
                "status": {"type": "integer", "description": "Статус: 2=новая, 3=в работе, 4=ожидает, 5=завершена, 6=отклонена"}
            }
        }
    },
    {
        "name": "tasks_create",
        "description": "Создать задачу в Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Название задачи"},
                "description": {"type": "string", "description": "Описание"},
                "responsible_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "deadline": {"type": "string", "description": "Дедлайн в формате 2026-06-30T18:00:00"},
                "priority": {"type": "integer", "description": "Приоритет: 0=низкий, 1=средний, 2=высокий"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "tasks_update",
        "description": "Обновить задачу: изменить название, статус, дедлайн, ответственного",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID задачи"},
                "title": {"type": "string", "description": "Новое название"},
                "description": {"type": "string", "description": "Описание"},
                "responsible_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "deadline": {"type": "string", "description": "Дедлайн в формате 2026-06-30T18:00:00"},
                "priority": {"type": "integer", "description": "Приоритет: 0=низкий, 1=средний, 2=высокий"},
                "status": {"type": "integer", "description": "Статус: 2=новая, 3=в работе, 4=ожидает, 5=завершена, 6=отклонена"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "tasks_delete",
        "description": "Удалить задачу по ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID задачи"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "tasks_complete",
        "description": "Завершить задачу (отметить как выполненную)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID задачи"}
            },
            "required": ["task_id"]
        }
    },

    # ───────────── ЗВОНКИ ─────────────
    {
        "name": "telephony_get_calls",
        "description": "Получить статистику звонков из Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество записей", "default": 20},
                "date_from": {"type": "string", "description": "Дата от (2026-05-01)"},
                "date_to": {"type": "string", "description": "Дата до (2026-05-31)"},
                "user_id": {"type": "integer", "description": "Фильтр по ID сотрудника"},
                "call_type": {"type": "integer", "description": "Тип звонка: 1=исходящий, 2=входящий"}
            }
        }
    },
    {
        "name": "telephony_get_call",
        "description": "Получить детали одного звонка по ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "call_id": {"type": "string", "description": "ID звонка"}
            },
            "required": ["call_id"]
        }
    },

    # ───────────── СОТРУДНИКИ ─────────────
    {
        "name": "users_get",
        "description": "Получить список сотрудников Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "active_only": {"type": "boolean", "description": "Только активные", "default": True}
            }
        }
    }
]


async def call_tool(name: str, args: dict) -> str:
    try:

        # ───────────── ЛИДЫ ─────────────
        if name == "crm_get_leads":
            filter_params = {}
            if args.get("status_id"): filter_params["STATUS_ID"] = args["status_id"]
            r = await b24("crm.lead.list", {
                "order": {"DATE_CREATE": "DESC"},
                "filter": filter_params,
                "select": ["ID", "TITLE", "NAME", "LAST_NAME", "PHONE", "EMAIL",
                           "STATUS_ID", "ASSIGNED_BY_ID", "DATE_CREATE", "COMMENTS"],
                "limit": args.get("limit", 20)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_lead":
            r = await b24("crm.lead.get", {"id": args["lead_id"]})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "crm_create_lead":
            fields = {"TITLE": args["title"]}
            if args.get("name"): fields["NAME"] = args["name"]
            if args.get("last_name"): fields["LAST_NAME"] = args["last_name"]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            if args.get("status_id"): fields["STATUS_ID"] = args["status_id"]
            if args.get("assigned_by_id"): fields["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("comment"): fields["COMMENTS"] = args["comment"]
            r = await b24("crm.lead.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_update_lead":
            fields = {}
            if args.get("title"): fields["TITLE"] = args["title"]
            if args.get("name"): fields["NAME"] = args["name"]
            if args.get("last_name"): fields["LAST_NAME"] = args["last_name"]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            if args.get("status_id"): fields["STATUS_ID"] = args["status_id"]
            if args.get("assigned_by_id"): fields["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("comment"): fields["COMMENTS"] = args["comment"]
            if not fields:
                return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("crm.lead.update", {"id": args["lead_id"], "fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_lead":
            r = await b24("crm.lead.delete", {"id": args["lead_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_get_lead_statuses":
            r = await b24("crm.status.list", {"filter": {"ENTITY_ID": "STATUS"}})
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        # ───────────── СДЕЛКИ ─────────────
        elif name == "crm_get_deals":
            filter_params = {}
            if args.get("stage_id"): filter_params["STAGE_ID"] = args["stage_id"]
            r = await b24("crm.deal.list", {
                "order": {"DATE_CREATE": "DESC"},
                "filter": filter_params,
                "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "ASSIGNED_BY_ID",
                           "CONTACT_ID", "COMPANY_ID", "DATE_CREATE", "COMMENTS"],
                "limit": args.get("limit", 20)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_deal":
            r = await b24("crm.deal.get", {"id": args["deal_id"]})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "crm_create_deal":
            fields = {"TITLE": args["title"]}
            if args.get("stage_id"): fields["STAGE_ID"] = args["stage_id"]
            if args.get("opportunity"): fields["OPPORTUNITY"] = args["opportunity"]
            if args.get("assigned_by_id"): fields["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("contact_id"): fields["CONTACT_ID"] = args["contact_id"]
            if args.get("company_id"): fields["COMPANY_ID"] = args["company_id"]
            if args.get("comment"): fields["COMMENTS"] = args["comment"]
            r = await b24("crm.deal.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_update_deal":
            fields = {}
            if args.get("title"): fields["TITLE"] = args["title"]
            if args.get("stage_id"): fields["STAGE_ID"] = args["stage_id"]
            if args.get("opportunity"): fields["OPPORTUNITY"] = args["opportunity"]
            if args.get("assigned_by_id"): fields["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("comment"): fields["COMMENTS"] = args["comment"]
            if not fields:
                return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("crm.deal.update", {"id": args["deal_id"], "fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_deal":
            r = await b24("crm.deal.delete", {"id": args["deal_id"]})
            return json.dumps(r, ensure_ascii=False)

        # ───────────── ЗАДАЧИ ─────────────
        elif name == "tasks_get":
            filter_params = {}
            if args.get("responsible_id"): filter_params["RESPONSIBLE_ID"] = args["responsible_id"]
            if args.get("status"): filter_params["STATUS"] = args["status"]
            r = await b24("tasks.task.list", {
                "order": {"CREATED_DATE": "desc"},
                "filter": filter_params,
                "select": ["ID", "TITLE", "STATUS", "RESPONSIBLE_ID", "DEADLINE",
                           "DESCRIPTION", "PRIORITY", "CREATED_DATE"],
                "params": {"NAV_PARAMS": {"nPageSize": args.get("limit", 20)}}
            })
            return json.dumps(r.get("result", {}).get("tasks", []), ensure_ascii=False, indent=2)

        elif name == "tasks_create":
            fields = {"TITLE": args["title"]}
            if args.get("description"): fields["DESCRIPTION"] = args["description"]
            if args.get("responsible_id"): fields["RESPONSIBLE_ID"] = args["responsible_id"]
            if args.get("deadline"): fields["DEADLINE"] = args["deadline"]
            if args.get("priority") is not None: fields["PRIORITY"] = args["priority"]
            r = await b24("tasks.task.add", {"fields": fields})
            return json.dumps(r.get("result", {}), ensure_ascii=False)

        elif name == "tasks_update":
            fields = {}
            if args.get("title"): fields["TITLE"] = args["title"]
            if args.get("description"): fields["DESCRIPTION"] = args["description"]
            if args.get("responsible_id"): fields["RESPONSIBLE_ID"] = args["responsible_id"]
            if args.get("deadline"): fields["DEADLINE"] = args["deadline"]
            if args.get("priority") is not None: fields["PRIORITY"] = args["priority"]
            if args.get("status") is not None: fields["STATUS"] = args["status"]
            if not fields:
                return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("tasks.task.update", {"taskId": args["task_id"], "fields": fields})
            return json.dumps(r.get("result", {}), ensure_ascii=False)

        elif name == "tasks_delete":
            r = await b24("tasks.task.delete", {"taskId": args["task_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "tasks_complete":
            r = await b24("tasks.task.complete", {"taskId": args["task_id"]})
            return json.dumps(r, ensure_ascii=False)

        # ───────────── ЗВОНКИ ─────────────
        elif name == "telephony_get_calls":
            filter_params = {}
            if args.get("date_from"): filter_params[">CALL_START_DATE"] = args["date_from"]
            if args.get("date_to"): filter_params["<CALL_START_DATE"] = args["date_to"]
            if args.get("user_id"): filter_params["PORTAL_USER_ID"] = args["user_id"]
            if args.get("call_type"): filter_params["CALL_TYPE"] = args["call_type"]
            r = await b24("voximplant.statistic.get", {
                "filter": filter_params,
                "select": ["ID", "PORTAL_USER_ID", "CALL_TYPE", "CALL_DURATION",
                           "CALL_START_DATE", "PHONE_NUMBER", "PORTAL_NUMBER",
                           "CALL_FAILED_CODE", "CRM_ENTITY_TYPE", "CRM_ENTITY_ID",
                           "RECORD_FILE_ID", "COST"],
                "limit": args.get("limit", 20)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "telephony_get_call":
            r = await b24("voximplant.statistic.get", {
                "filter": {"CALL_ID": args["call_id"]},
                "select": ["ID", "PORTAL_USER_ID", "CALL_TYPE", "CALL_DURATION",
                           "CALL_START_DATE", "PHONE_NUMBER", "PORTAL_NUMBER",
                           "CALL_FAILED_CODE", "CRM_ENTITY_TYPE", "CRM_ENTITY_ID",
                           "RECORD_FILE_ID", "COST", "CALL_VOTE"]
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        # ───────────── СОТРУДНИКИ ─────────────
        elif name == "users_get":
            params = {"select": ["ID", "NAME", "LAST_NAME", "EMAIL", "WORK_PHONE", "ACTIVE"]}
            if args.get("active_only", True):
                params["filter"] = {"ACTIVE": True}
            r = await b24("user.get", params)
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        else:
            return f"Unknown tool: {name}"

    except Exception as e:
        return f"Error: {str(e)}"


async def handle_rpc(data: dict) -> dict:
    method = data.get("method")
    req_id = data.get("id")
    params = data.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "bitrix24-mcp", "version": "2.0.0"}
            }
        }
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        result = await call_tool(tool_name, tool_args)
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"content": [{"type": "text", "text": result}]}
        }
    else:
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}


@app.get("/sse")
async def sse_get(request: Request):
    async def event_stream():
        yield f"data: {json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'})}\n\n"
        try:
            async for chunk in request.stream():
                if chunk:
                    try:
                        data = json.loads(chunk)
                        response = await handle_rpc(data)
                        yield f"data: {json.dumps(response)}\n\n"
                    except Exception:
                        pass
        except Exception:
            pass

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/sse")
async def sse_post(request: Request):
    data = await request.json()
    response = await handle_rpc(data)
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
