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
    {
        "name": "crm_get_leads",
        "description": "Получить список лидов из CRM Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество лидов", "default": 20}
            }
        }
    },
    {
        "name": "crm_get_deals",
        "description": "Получить список сделок из CRM Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество сделок", "default": 20}
            }
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
                "email": {"type": "string", "description": "Email"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "tasks_get",
        "description": "Получить список задач из Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество задач", "default": 20}
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
                "deadline": {"type": "string", "description": "Дедлайн в формате 2026-06-30T18:00:00"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "users_get",
        "description": "Получить список сотрудников Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "active_only": {"type": "boolean", "description": "Только активные", "default": True}
            }
        }
    },
    {
        "name": "telephony_get_calls",
        "description": "Получить статистику звонков из Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество записей", "default": 20},
                "date_from": {"type": "string", "description": "Дата от (2026-05-01)"},
                "date_to": {"type": "string", "description": "Дата до (2026-05-31)"}
            }
        }
    }
]

async def call_tool(name: str, args: dict) -> str:
    try:
        if name == "crm_get_leads":
            r = await b24("crm.lead.list", {
                "order": {"DATE_CREATE": "DESC"},
                "select": ["ID", "TITLE", "NAME", "LAST_NAME", "PHONE", "STATUS_ID", "DATE_CREATE"],
                "limit": args.get("limit", 20)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_deals":
            r = await b24("crm.deal.list", {
                "order": {"DATE_CREATE": "DESC"},
                "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY", "DATE_CREATE"],
                "limit": args.get("limit", 20)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_create_lead":
            fields = {"TITLE": args["title"]}
            if args.get("name"): fields["NAME"] = args["name"]
            if args.get("last_name"): fields["LAST_NAME"] = args["last_name"]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            r = await b24("crm.lead.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "tasks_get":
            r = await b24("tasks.task.list", {
                "order": {"CREATED_DATE": "desc"},
                "select": ["ID", "TITLE", "STATUS", "RESPONSIBLE_ID", "DEADLINE"],
                "params": {"NAV_PARAMS": {"nPageSize": args.get("limit", 20)}}
            })
            return json.dumps(r.get("result", {}).get("tasks", []), ensure_ascii=False, indent=2)

        elif name == "tasks_create":
            fields = {"TITLE": args["title"]}
            if args.get("description"): fields["DESCRIPTION"] = args["description"]
            if args.get("deadline"): fields["DEADLINE"] = args["deadline"]
            r = await b24("tasks.task.add", {"fields": fields})
            return json.dumps(r.get("result", {}), ensure_ascii=False)

        elif name == "users_get":
            params = {"select": ["ID", "NAME", "LAST_NAME", "EMAIL", "WORK_PHONE", "ACTIVE"]}
            if args.get("active_only", True):
                params["filter"] = {"ACTIVE": True}
            r = await b24("user.get", params)
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "telephony_get_calls":
            filter_params = {}
            if args.get("date_from"): filter_params[">CALL_START_DATE"] = args["date_from"]
            if args.get("date_to"): filter_params["<CALL_START_DATE"] = args["date_to"]
            r = await b24("voximplant.statistic.get", {
                "filter": filter_params,
                "select": ["ID", "PORTAL_USER_ID", "CALL_TYPE", "CALL_DURATION", "CALL_START_DATE", "PHONE_NUMBER"],
                "limit": args.get("limit", 20)
            })
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
                "serverInfo": {"name": "bitrix24-mcp", "version": "1.0.0"}
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
