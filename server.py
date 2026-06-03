import httpx
import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

BITRIX_WEBHOOK = os.environ.get("BITRIX_WEBHOOK", "").rstrip("/")

app = FastAPI()


async def b24(method: str, params: dict = {}) -> dict:
    url = f"{BITRIX_WEBHOOK}/{method}.json"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, json=params)
        r.raise_for_status()
        return r.json()


TOOLS = [

    # ═══════════════════════════════════════
    # ЛИДЫ
    # ═══════════════════════════════════════
    {
        "name": "crm_get_leads",
        "description": "Получить список лидов из CRM. Поддерживает фильтрацию по статусу, ответственному, дате создания, телефону, имени, источнику.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Количество лидов (по умолчанию 50)", "default": 50},
                "status_id": {"type": "string", "description": "Фильтр по стадии: NEW, IN_PROCESS, CONVERTED, JUNK и др."},
                "assigned_by_id": {"type": "integer", "description": "Фильтр по ответственному (ID сотрудника)"},
                "date_from": {"type": "string", "description": "Дата создания от (YYYY-MM-DD), например 2026-06-01"},
                "date_to": {"type": "string", "description": "Дата создания до (YYYY-MM-DD), например 2026-06-30"},
                "phone": {"type": "string", "description": "Поиск по номеру телефона"},
                "name": {"type": "string", "description": "Поиск по имени"},
                "last_name": {"type": "string", "description": "Поиск по фамилии"},
                "source_id": {"type": "string", "description": "Источник лида: CALL, WEB, EMAIL и др."},
                "title": {"type": "string", "description": "Поиск по названию лида"}
            }
        }
    },
    {
        "name": "crm_search_leads",
        "description": "Поиск лидов по любому тексту (имя, фамилия, телефон, email, название)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Поисковый запрос"},
                "limit": {"type": "integer", "description": "Количество результатов", "default": 20}
            },
            "required": ["query"]
        }
    },
    {
        "name": "crm_get_lead",
        "description": "Получить полную информацию по одному лиду по ID",
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
                "source_id": {"type": "string", "description": "Источник лида"},
                "comment": {"type": "string", "description": "Комментарий"},
                "opportunity": {"type": "number", "description": "Сумма"},
                "currency_id": {"type": "string", "description": "Валюта, например RUB"}
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
                "title": {"type": "string"},
                "name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "status_id": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "source_id": {"type": "string"},
                "comment": {"type": "string"},
                "opportunity": {"type": "number"},
                "currency_id": {"type": "string"}
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "crm_delete_lead",
        "description": "Удалить лид по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"lead_id": {"type": "integer"}},
            "required": ["lead_id"]
        }
    },
    {
        "name": "crm_get_lead_statuses",
        "description": "Получить список доступных стадий лидов",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "crm_get_lead_sources",
        "description": "Получить список источников лидов",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "crm_add_lead_comment",
        "description": "Добавить комментарий к лиду",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lead_id": {"type": "integer"},
                "comment": {"type": "string"}
            },
            "required": ["lead_id", "comment"]
        }
    },
    {
        "name": "crm_get_lead_timeline",
        "description": "Получить историю активностей по лиду (звонки, письма, комментарии)",
        "inputSchema": {
            "type": "object",
            "properties": {"lead_id": {"type": "integer"}},
            "required": ["lead_id"]
        }
    },

    # ═══════════════════════════════════════
    # СДЕЛКИ
    # ═══════════════════════════════════════
    {
        "name": "crm_get_deals",
        "description": "Получить список сделок из CRM с фильтрацией",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "stage_id": {"type": "string", "description": "Стадия сделки"},
                "assigned_by_id": {"type": "integer"},
                "date_from": {"type": "string", "description": "YYYY-MM-DD"},
                "date_to": {"type": "string", "description": "YYYY-MM-DD"},
                "contact_id": {"type": "integer"},
                "company_id": {"type": "integer"},
                "pipeline_id": {"type": "integer", "description": "ID воронки"}
            }
        }
    },
    {
        "name": "crm_get_deal",
        "description": "Получить одну сделку по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"deal_id": {"type": "integer"}},
            "required": ["deal_id"]
        }
    },
    {
        "name": "crm_create_deal",
        "description": "Создать новую сделку в CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "stage_id": {"type": "string"},
                "opportunity": {"type": "number"},
                "currency_id": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "contact_id": {"type": "integer"},
                "company_id": {"type": "integer"},
                "comment": {"type": "string"},
                "pipeline_id": {"type": "integer"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "crm_update_deal",
        "description": "Обновить сделку: стадию, ответственного, сумму и другие поля",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "integer"},
                "title": {"type": "string"},
                "stage_id": {"type": "string"},
                "opportunity": {"type": "number"},
                "currency_id": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "contact_id": {"type": "integer"},
                "company_id": {"type": "integer"},
                "comment": {"type": "string"}
            },
            "required": ["deal_id"]
        }
    },
    {
        "name": "crm_delete_deal",
        "description": "Удалить сделку по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"deal_id": {"type": "integer"}},
            "required": ["deal_id"]
        }
    },
    {
        "name": "crm_get_deal_stages",
        "description": "Получить стадии воронки сделок",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pipeline_id": {"type": "integer", "description": "ID воронки (0 = основная)"}
            }
        }
    },
    {
        "name": "crm_get_pipelines",
        "description": "Получить список воронок сделок",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "crm_add_deal_comment",
        "description": "Добавить комментарий к сделке",
        "inputSchema": {
            "type": "object",
            "properties": {
                "deal_id": {"type": "integer"},
                "comment": {"type": "string"}
            },
            "required": ["deal_id", "comment"]
        }
    },
    {
        "name": "crm_get_deal_timeline",
        "description": "Получить историю активностей по сделке",
        "inputSchema": {
            "type": "object",
            "properties": {"deal_id": {"type": "integer"}},
            "required": ["deal_id"]
        }
    },

    # ═══════════════════════════════════════
    # КОНТАКТЫ
    # ═══════════════════════════════════════
    {
        "name": "crm_get_contacts",
        "description": "Получить список контактов из CRM с фильтрацией",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "assigned_by_id": {"type": "integer"},
                "name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "date_from": {"type": "string"},
                "date_to": {"type": "string"}
            }
        }
    },
    {
        "name": "crm_get_contact",
        "description": "Получить полную информацию по контакту по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"contact_id": {"type": "integer"}},
            "required": ["contact_id"]
        }
    },
    {
        "name": "crm_create_contact",
        "description": "Создать новый контакт в CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "company_id": {"type": "integer"},
                "post": {"type": "string", "description": "Должность"},
                "comment": {"type": "string"}
            }
        }
    },
    {
        "name": "crm_update_contact",
        "description": "Обновить контакт",
        "inputSchema": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "integer"},
                "name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "company_id": {"type": "integer"},
                "post": {"type": "string"},
                "comment": {"type": "string"}
            },
            "required": ["contact_id"]
        }
    },
    {
        "name": "crm_delete_contact",
        "description": "Удалить контакт по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"contact_id": {"type": "integer"}},
            "required": ["contact_id"]
        }
    },

    # ═══════════════════════════════════════
    # КОМПАНИИ
    # ═══════════════════════════════════════
    {
        "name": "crm_get_companies",
        "description": "Получить список компаний из CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "assigned_by_id": {"type": "integer"},
                "title": {"type": "string", "description": "Поиск по названию"},
                "phone": {"type": "string"},
                "date_from": {"type": "string"},
                "date_to": {"type": "string"}
            }
        }
    },
    {
        "name": "crm_get_company",
        "description": "Получить полную информацию по компании по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"company_id": {"type": "integer"}},
            "required": ["company_id"]
        }
    },
    {
        "name": "crm_create_company",
        "description": "Создать новую компанию в CRM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "industry": {"type": "string"},
                "employees": {"type": "integer"},
                "comment": {"type": "string"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "crm_update_company",
        "description": "Обновить компанию",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_id": {"type": "integer"},
                "title": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "assigned_by_id": {"type": "integer"},
                "industry": {"type": "string"},
                "comment": {"type": "string"}
            },
            "required": ["company_id"]
        }
    },
    {
        "name": "crm_delete_company",
        "description": "Удалить компанию по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"company_id": {"type": "integer"}},
            "required": ["company_id"]
        }
    },

    # ═══════════════════════════════════════
    # АКТИВНОСТИ / ДЕЛА
    # ═══════════════════════════════════════
    {
        "name": "crm_get_activities",
        "description": "Получить список дел/активностей CRM (звонки, встречи, письма, задачи CRM)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "owner_type_id": {"type": "integer", "description": "Тип владельца: 1=Лид, 2=Сделка, 3=Контакт, 4=Компания"},
                "owner_id": {"type": "integer", "description": "ID владельца (лида, сделки и т.д.)"},
                "type_id": {"type": "integer", "description": "Тип активности: 1=встреча, 2=звонок, 3=задача, 4=событие, 6=email"},
                "assigned_by_id": {"type": "integer"},
                "date_from": {"type": "string"},
                "date_to": {"type": "string"},
                "completed": {"type": "boolean", "description": "Только завершённые (true) или незавершённые (false)"}
            }
        }
    },
    {
        "name": "crm_create_activity",
        "description": "Создать дело/активность в CRM (звонок, встреча, задача, письмо)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Тема/название"},
                "type_id": {"type": "integer", "description": "Тип: 1=встреча, 2=звонок, 3=задача CRM, 6=email"},
                "owner_type_id": {"type": "integer", "description": "Тип владельца: 1=Лид, 2=Сделка, 3=Контакт, 4=Компания"},
                "owner_id": {"type": "integer", "description": "ID владельца"},
                "description": {"type": "string"},
                "start_time": {"type": "string", "description": "Начало: 2026-06-03T10:00:00"},
                "end_time": {"type": "string", "description": "Конец: 2026-06-03T11:00:00"},
                "deadline": {"type": "string", "description": "Дедлайн: 2026-06-03T18:00:00"},
                "responsible_id": {"type": "integer"},
                "priority": {"type": "string", "description": "Приоритет: 0=низкий, 1=средний, 2=высокий"}
            },
            "required": ["subject", "type_id", "owner_type_id", "owner_id"]
        }
    },
    {
        "name": "crm_complete_activity",
        "description": "Завершить дело/активность",
        "inputSchema": {
            "type": "object",
            "properties": {"activity_id": {"type": "integer"}},
            "required": ["activity_id"]
        }
    },
    {
        "name": "crm_delete_activity",
        "description": "Удалить дело/активность по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"activity_id": {"type": "integer"}},
            "required": ["activity_id"]
        }
    },

    # ═══════════════════════════════════════
    # ЗАДАЧИ
    # ═══════════════════════════════════════
    {
        "name": "tasks_get",
        "description": "Получить список задач из Битрикс24 с фильтрацией по ответственному, постановщику, статусу, дате создания, дедлайну, названию",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "responsible_id": {"type": "integer", "description": "ID ответственного сотрудника"},
                "created_by_id": {"type": "integer", "description": "ID постановщика задачи"},
                "status": {"type": "integer", "description": "Статус: 2=новая, 3=в работе, 4=ожидает, 5=завершена, 6=отклонена"},
                "date_from": {"type": "string", "description": "Дата создания от (YYYY-MM-DD)"},
                "date_to": {"type": "string", "description": "Дата создания до (YYYY-MM-DD)"},
                "deadline_from": {"type": "string", "description": "Дедлайн от (YYYY-MM-DD)"},
                "deadline_to": {"type": "string", "description": "Дедлайн до (YYYY-MM-DD)"},
                "title": {"type": "string", "description": "Поиск по названию задачи"},
                "group_id": {"type": "integer", "description": "ID группы/проекта"},
                "priority": {"type": "integer", "description": "Приоритет: 0=низкий, 1=средний, 2=высокий"}
            }
        }
    },
    {
        "name": "tasks_get_task",
        "description": "Получить полную информацию по задаче по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"]
        }
    },
    {
        "name": "tasks_create",
        "description": "Создать задачу в Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "responsible_id": {"type": "integer", "description": "ID ответственного"},
                "created_by": {"type": "integer", "description": "ID постановщика"},
                "deadline": {"type": "string", "description": "2026-06-30T18:00:00"},
                "start_date_plan": {"type": "string", "description": "Плановая дата начала"},
                "priority": {"type": "integer", "description": "0=низкий, 1=средний, 2=высокий"},
                "group_id": {"type": "integer", "description": "ID группы/проекта"},
                "auditors": {"type": "array", "items": {"type": "integer"}, "description": "ID наблюдателей"},
                "accomplices": {"type": "array", "items": {"type": "integer"}, "description": "ID соисполнителей"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "tasks_update",
        "description": "Обновить задачу: название, статус, дедлайн, ответственного, описание",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "responsible_id": {"type": "integer"},
                "deadline": {"type": "string"},
                "priority": {"type": "integer"},
                "status": {"type": "integer"},
                "group_id": {"type": "integer"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "tasks_complete",
        "description": "Завершить задачу (отметить как выполненную)",
        "inputSchema": {
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"]
        }
    },
    {
        "name": "tasks_delete",
        "description": "Удалить задачу по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"]
        }
    },
    {
        "name": "tasks_get_comments",
        "description": "Получить комментарии к задаче",
        "inputSchema": {
            "type": "object",
            "properties": {"task_id": {"type": "integer"}},
            "required": ["task_id"]
        }
    },
    {
        "name": "tasks_add_comment",
        "description": "Добавить комментарий к задаче",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "comment": {"type": "string"}
            },
            "required": ["task_id", "comment"]
        }
    },

    # ═══════════════════════════════════════
    # ЗВОНКИ
    # ═══════════════════════════════════════
    {
        "name": "telephony_get_calls",
        "description": "Получить статистику звонков с фильтрацией по дате, сотруднику, типу",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "date_from": {"type": "string", "description": "YYYY-MM-DD"},
                "date_to": {"type": "string", "description": "YYYY-MM-DD"},
                "user_id": {"type": "integer"},
                "call_type": {"type": "integer", "description": "1=исходящий, 2=входящий, 3=входящий с перенаправлением"},
                "phone_number": {"type": "string", "description": "Номер телефона"}
            }
        }
    },
    {
        "name": "telephony_get_call",
        "description": "Получить детали одного звонка по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"call_id": {"type": "string"}},
            "required": ["call_id"]
        }
    },

    # ═══════════════════════════════════════
    # СОТРУДНИКИ
    # ═══════════════════════════════════════
    {
        "name": "users_get",
        "description": "Получить список сотрудников Битрикс24 с фильтрацией",
        "inputSchema": {
            "type": "object",
            "properties": {
                "active_only": {"type": "boolean", "default": True},
                "name": {"type": "string", "description": "Поиск по имени"},
                "last_name": {"type": "string", "description": "Поиск по фамилии"},
                "department_id": {"type": "integer", "description": "ID отдела"}
            }
        }
    },
    {
        "name": "users_get_current",
        "description": "Получить текущего авторизованного пользователя",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "users_get_user",
        "description": "Получить сотрудника по ID",
        "inputSchema": {
            "type": "object",
            "properties": {"user_id": {"type": "integer"}},
            "required": ["user_id"]
        }
    },

    # ═══════════════════════════════════════
    # ОТДЕЛЫ
    # ═══════════════════════════════════════
    {
        "name": "departments_get",
        "description": "Получить список отделов компании в Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "parent_id": {"type": "integer", "description": "ID родительского отдела"}
            }
        }
    },

    # ═══════════════════════════════════════
    # ЧАТЫ / УВЕДОМЛЕНИЯ
    # ═══════════════════════════════════════
    {
        "name": "send_notification",
        "description": "Отправить уведомление (сообщение) сотруднику в Битрикс24",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID получателя"},
                "message": {"type": "string", "description": "Текст сообщения"}
            },
            "required": ["user_id", "message"]
        }
    },

    # ═══════════════════════════════════════
    # УНИВЕРСАЛЬНЫЙ ВЫЗОВ
    # ═══════════════════════════════════════
    {
        "name": "bitrix_call",
        "description": "Вызвать любой метод Битрикс24 API напрямую. Используй когда нет подходящего инструмента.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "description": "Метод API, например crm.lead.list, tasks.task.list"},
                "params": {"type": "object", "description": "Параметры запроса"}
            },
            "required": ["method"]
        }
    }
]


async def call_tool(name: str, args: dict) -> str:
    try:

        # ─── ЛИДЫ ───────────────────────────────────────
        if name == "crm_get_leads":
            f = {}
            if args.get("status_id"):     f["STATUS_ID"] = args["status_id"]
            if args.get("assigned_by_id"): f["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("date_from"):      f[">=DATE_CREATE"] = args["date_from"] + "T00:00:00"
            if args.get("date_to"):        f["<=DATE_CREATE"] = args["date_to"] + "T23:59:59"
            if args.get("phone"):          f["%PHONE"] = args["phone"]
            if args.get("name"):           f["%NAME"] = args["name"]
            if args.get("last_name"):      f["%LAST_NAME"] = args["last_name"]
            if args.get("source_id"):      f["SOURCE_ID"] = args["source_id"]
            if args.get("title"):          f["%TITLE"] = args["title"]
            r = await b24("crm.lead.list", {
                "order": {"DATE_CREATE": "DESC"},
                "filter": f,
                "select": ["ID", "TITLE", "NAME", "LAST_NAME", "PHONE", "EMAIL",
                           "STATUS_ID", "ASSIGNED_BY_ID", "DATE_CREATE", "COMMENTS",
                           "SOURCE_ID", "UTM_SOURCE", "UTM_MEDIUM", "OPPORTUNITY"],
                "limit": args.get("limit", 50)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_search_leads":
            q = args["query"]
            r1 = await b24("crm.lead.list", {"order": {"DATE_CREATE": "DESC"}, "filter": {"%TITLE": q},
                "select": ["ID","TITLE","NAME","LAST_NAME","PHONE","EMAIL","STATUS_ID","ASSIGNED_BY_ID","DATE_CREATE"],
                "limit": args.get("limit", 20)})
            r2 = await b24("crm.lead.list", {"order": {"DATE_CREATE": "DESC"}, "filter": {"%NAME": q},
                "select": ["ID","TITLE","NAME","LAST_NAME","PHONE","EMAIL","STATUS_ID","ASSIGNED_BY_ID","DATE_CREATE"],
                "limit": args.get("limit", 20)})
            r3 = await b24("crm.lead.list", {"order": {"DATE_CREATE": "DESC"}, "filter": {"%LAST_NAME": q},
                "select": ["ID","TITLE","NAME","LAST_NAME","PHONE","EMAIL","STATUS_ID","ASSIGNED_BY_ID","DATE_CREATE"],
                "limit": args.get("limit", 20)})
            seen, results = set(), []
            for lst in [r1.get("result",[]), r2.get("result",[]), r3.get("result",[])]:
                for item in lst:
                    if item["ID"] not in seen:
                        seen.add(item["ID"])
                        results.append(item)
            return json.dumps(results[:args.get("limit", 20)], ensure_ascii=False, indent=2)

        elif name == "crm_get_lead":
            r = await b24("crm.lead.get", {"id": args["lead_id"]})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "crm_create_lead":
            fields = {"TITLE": args["title"]}
            for k, v in [("name","NAME"),("last_name","LAST_NAME"),("status_id","STATUS_ID"),
                         ("assigned_by_id","ASSIGNED_BY_ID"),("source_id","SOURCE_ID"),
                         ("comment","COMMENTS"),("opportunity","OPPORTUNITY"),("currency_id","CURRENCY_ID")]:
                if args.get(k): fields[v] = args[k]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            r = await b24("crm.lead.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_update_lead":
            fields = {}
            for k, v in [("title","TITLE"),("name","NAME"),("last_name","LAST_NAME"),
                         ("status_id","STATUS_ID"),("assigned_by_id","ASSIGNED_BY_ID"),
                         ("source_id","SOURCE_ID"),("comment","COMMENTS"),
                         ("opportunity","OPPORTUNITY"),("currency_id","CURRENCY_ID")]:
                if args.get(k): fields[v] = args[k]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            if not fields: return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("crm.lead.update", {"id": args["lead_id"], "fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_lead":
            r = await b24("crm.lead.delete", {"id": args["lead_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_get_lead_statuses":
            r = await b24("crm.status.list", {"filter": {"ENTITY_ID": "STATUS"}})
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_lead_sources":
            r = await b24("crm.status.list", {"filter": {"ENTITY_ID": "SOURCE"}})
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_add_lead_comment":
            r = await b24("crm.timeline.comment.add", {
                "fields": {"ENTITY_ID": args["lead_id"], "ENTITY_TYPE": "lead", "COMMENT": args["comment"]}
            })
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_get_lead_timeline":
            r = await b24("crm.timeline.comment.list", {
                "filter": {"ENTITY_ID": args["lead_id"], "ENTITY_TYPE": "lead"}
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        # ─── СДЕЛКИ ─────────────────────────────────────
        elif name == "crm_get_deals":
            f = {}
            if args.get("stage_id"):       f["STAGE_ID"] = args["stage_id"]
            if args.get("assigned_by_id"): f["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("date_from"):      f[">=DATE_CREATE"] = args["date_from"] + "T00:00:00"
            if args.get("date_to"):        f["<=DATE_CREATE"] = args["date_to"] + "T23:59:59"
            if args.get("contact_id"):     f["CONTACT_ID"] = args["contact_id"]
            if args.get("company_id"):     f["COMPANY_ID"] = args["company_id"]
            if args.get("pipeline_id") is not None: f["CATEGORY_ID"] = args["pipeline_id"]
            r = await b24("crm.deal.list", {
                "order": {"DATE_CREATE": "DESC"},
                "filter": f,
                "select": ["ID","TITLE","STAGE_ID","OPPORTUNITY","CURRENCY_ID","ASSIGNED_BY_ID",
                           "CONTACT_ID","COMPANY_ID","DATE_CREATE","COMMENTS","CATEGORY_ID"],
                "limit": args.get("limit", 50)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_deal":
            r = await b24("crm.deal.get", {"id": args["deal_id"]})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "crm_create_deal":
            fields = {"TITLE": args["title"]}
            for k, v in [("stage_id","STAGE_ID"),("opportunity","OPPORTUNITY"),("currency_id","CURRENCY_ID"),
                         ("assigned_by_id","ASSIGNED_BY_ID"),("contact_id","CONTACT_ID"),
                         ("company_id","COMPANY_ID"),("comment","COMMENTS"),("pipeline_id","CATEGORY_ID")]:
                if args.get(k) is not None: fields[v] = args[k]
            r = await b24("crm.deal.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_update_deal":
            fields = {}
            for k, v in [("title","TITLE"),("stage_id","STAGE_ID"),("opportunity","OPPORTUNITY"),
                         ("currency_id","CURRENCY_ID"),("assigned_by_id","ASSIGNED_BY_ID"),
                         ("contact_id","CONTACT_ID"),("company_id","COMPANY_ID"),("comment","COMMENTS")]:
                if args.get(k) is not None: fields[v] = args[k]
            if not fields: return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("crm.deal.update", {"id": args["deal_id"], "fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_deal":
            r = await b24("crm.deal.delete", {"id": args["deal_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_get_deal_stages":
            params = {}
            if args.get("pipeline_id") is not None:
                params["id"] = args["pipeline_id"]
            r = await b24("crm.dealcategory.stage.list", params)
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_pipelines":
            r = await b24("crm.dealcategory.list", {})
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_add_deal_comment":
            r = await b24("crm.timeline.comment.add", {
                "fields": {"ENTITY_ID": args["deal_id"], "ENTITY_TYPE": "deal", "COMMENT": args["comment"]}
            })
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_get_deal_timeline":
            r = await b24("crm.timeline.comment.list", {
                "filter": {"ENTITY_ID": args["deal_id"], "ENTITY_TYPE": "deal"}
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        # ─── КОНТАКТЫ ───────────────────────────────────
        elif name == "crm_get_contacts":
            f = {}
            if args.get("assigned_by_id"): f["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("name"):     f["%NAME"] = args["name"]
            if args.get("last_name"): f["%LAST_NAME"] = args["last_name"]
            if args.get("phone"):    f["%PHONE"] = args["phone"]
            if args.get("email"):    f["%EMAIL"] = args["email"]
            if args.get("date_from"): f[">=DATE_CREATE"] = args["date_from"] + "T00:00:00"
            if args.get("date_to"):   f["<=DATE_CREATE"] = args["date_to"] + "T23:59:59"
            r = await b24("crm.contact.list", {
                "order": {"DATE_CREATE": "DESC"},
                "filter": f,
                "select": ["ID","NAME","LAST_NAME","PHONE","EMAIL","ASSIGNED_BY_ID",
                           "COMPANY_ID","DATE_CREATE","POST","COMMENTS"],
                "limit": args.get("limit", 50)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_contact":
            r = await b24("crm.contact.get", {"id": args["contact_id"]})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "crm_create_contact":
            fields = {}
            for k, v in [("name","NAME"),("last_name","LAST_NAME"),("assigned_by_id","ASSIGNED_BY_ID"),
                         ("company_id","COMPANY_ID"),("post","POST"),("comment","COMMENTS")]:
                if args.get(k): fields[v] = args[k]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            r = await b24("crm.contact.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_update_contact":
            fields = {}
            for k, v in [("name","NAME"),("last_name","LAST_NAME"),("assigned_by_id","ASSIGNED_BY_ID"),
                         ("company_id","COMPANY_ID"),("post","POST"),("comment","COMMENTS")]:
                if args.get(k): fields[v] = args[k]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            if not fields: return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("crm.contact.update", {"id": args["contact_id"], "fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_contact":
            r = await b24("crm.contact.delete", {"id": args["contact_id"]})
            return json.dumps(r, ensure_ascii=False)

        # ─── КОМПАНИИ ───────────────────────────────────
        elif name == "crm_get_companies":
            f = {}
            if args.get("assigned_by_id"): f["ASSIGNED_BY_ID"] = args["assigned_by_id"]
            if args.get("title"):   f["%TITLE"] = args["title"]
            if args.get("phone"):   f["%PHONE"] = args["phone"]
            if args.get("date_from"): f[">=DATE_CREATE"] = args["date_from"] + "T00:00:00"
            if args.get("date_to"):   f["<=DATE_CREATE"] = args["date_to"] + "T23:59:59"
            r = await b24("crm.company.list", {
                "order": {"DATE_CREATE": "DESC"},
                "filter": f,
                "select": ["ID","TITLE","PHONE","EMAIL","ASSIGNED_BY_ID",
                           "DATE_CREATE","INDUSTRY","EMPLOYEES","COMMENTS"],
                "limit": args.get("limit", 50)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_get_company":
            r = await b24("crm.company.get", {"id": args["company_id"]})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "crm_create_company":
            fields = {"TITLE": args["title"]}
            for k, v in [("assigned_by_id","ASSIGNED_BY_ID"),("industry","INDUSTRY"),
                         ("employees","EMPLOYEES"),("comment","COMMENTS")]:
                if args.get(k): fields[v] = args[k]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            r = await b24("crm.company.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_update_company":
            fields = {}
            for k, v in [("title","TITLE"),("assigned_by_id","ASSIGNED_BY_ID"),
                         ("industry","INDUSTRY"),("comment","COMMENTS")]:
                if args.get(k): fields[v] = args[k]
            if args.get("phone"): fields["PHONE"] = [{"VALUE": args["phone"], "VALUE_TYPE": "WORK"}]
            if args.get("email"): fields["EMAIL"] = [{"VALUE": args["email"], "VALUE_TYPE": "WORK"}]
            if not fields: return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("crm.company.update", {"id": args["company_id"], "fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_company":
            r = await b24("crm.company.delete", {"id": args["company_id"]})
            return json.dumps(r, ensure_ascii=False)

        # ─── АКТИВНОСТИ ─────────────────────────────────
        elif name == "crm_get_activities":
            f = {}
            if args.get("owner_type_id"): f["OWNER_TYPE_ID"] = args["owner_type_id"]
            if args.get("owner_id"):      f["OWNER_ID"] = args["owner_id"]
            if args.get("type_id"):       f["TYPE_ID"] = args["type_id"]
            if args.get("assigned_by_id"): f["RESPONSIBLE_ID"] = args["assigned_by_id"]
            if args.get("date_from"):     f[">=DEADLINE"] = args["date_from"] + "T00:00:00"
            if args.get("date_to"):       f["<=DEADLINE"] = args["date_to"] + "T23:59:59"
            if args.get("completed") is not None:
                f["COMPLETED"] = "Y" if args["completed"] else "N"
            r = await b24("crm.activity.list", {
                "order": {"ID": "DESC"},
                "filter": f,
                "select": ["ID","SUBJECT","TYPE_ID","OWNER_ID","OWNER_TYPE_ID","RESPONSIBLE_ID",
                           "DEADLINE","DESCRIPTION","COMPLETED","PRIORITY","CREATED","START_TIME","END_TIME"],
                "limit": args.get("limit", 50)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "crm_create_activity":
            fields = {
                "SUBJECT": args["subject"],
                "TYPE_ID": args["type_id"],
                "OWNER_TYPE_ID": args["owner_type_id"],
                "OWNER_ID": args["owner_id"],
                "COMPLETED": "N"
            }
            for k, v in [("description","DESCRIPTION"),("start_time","START_TIME"),
                         ("end_time","END_TIME"),("deadline","DEADLINE"),
                         ("responsible_id","RESPONSIBLE_ID"),("priority","PRIORITY")]:
                if args.get(k) is not None: fields[v] = args[k]
            r = await b24("crm.activity.add", {"fields": fields})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_complete_activity":
            r = await b24("crm.activity.complete", {"id": args["activity_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "crm_delete_activity":
            r = await b24("crm.activity.delete", {"id": args["activity_id"]})
            return json.dumps(r, ensure_ascii=False)

        # ─── ЗАДАЧИ ─────────────────────────────────────
        elif name == "tasks_get":
            f = {}
            if args.get("responsible_id"): f["RESPONSIBLE_ID"] = args["responsible_id"]
            if args.get("created_by_id"):  f["CREATED_BY"] = args["created_by_id"]
            if args.get("status") is not None: f["STATUS"] = args["status"]
            if args.get("date_from"):      f[">=CREATED_DATE"] = args["date_from"] + "T00:00:00"
            if args.get("date_to"):        f["<=CREATED_DATE"] = args["date_to"] + "T23:59:59"
            if args.get("deadline_from"):  f[">=DEADLINE"] = args["deadline_from"] + "T00:00:00"
            if args.get("deadline_to"):    f["<=DEADLINE"] = args["deadline_to"] + "T23:59:59"
            if args.get("title"):          f["%TITLE"] = args["title"]
            if args.get("group_id"):       f["GROUP_ID"] = args["group_id"]
            if args.get("priority") is not None: f["PRIORITY"] = args["priority"]
            r = await b24("tasks.task.list", {
                "order": {"CREATED_DATE": "desc"},
                "filter": f,
                "select": ["ID","TITLE","STATUS","RESPONSIBLE_ID","CREATED_BY",
                           "DEADLINE","DESCRIPTION","PRIORITY","CREATED_DATE","GROUP_ID"],
                "params": {"NAV_PARAMS": {"nPageSize": args.get("limit", 50)}}
            })
            return json.dumps(r.get("result", {}).get("tasks", []), ensure_ascii=False, indent=2)

        elif name == "tasks_get_task":
            r = await b24("tasks.task.get", {"taskId": args["id"],
                "select": ["ID","TITLE","STATUS","RESPONSIBLE_ID","CREATED_BY","DEADLINE",
                           "DESCRIPTION","PRIORITY","CREATED_DATE","GROUP_ID","AUDITORS","ACCOMPLICES"]})
            return json.dumps(r.get("result", {}).get("task", {}), ensure_ascii=False, indent=2)

        elif name == "tasks_create":
            fields = {"TITLE": args["title"]}
            for k, v in [("description","DESCRIPTION"),("responsible_id","RESPONSIBLE_ID"),
                         ("created_by","CREATED_BY"),("deadline","DEADLINE"),
                         ("start_date_plan","START_DATE_PLAN"),("group_id","GROUP_ID")]:
                if args.get(k): fields[v] = args[k]
            if args.get("priority") is not None: fields["PRIORITY"] = args["priority"]
            if args.get("auditors"):     fields["AUDITORS"] = args["auditors"]
            if args.get("accomplices"):  fields["ACCOMPLICES"] = args["accomplices"]
            r = await b24("tasks.task.add", {"fields": fields})
            return json.dumps(r.get("result", {}), ensure_ascii=False)

        elif name == "tasks_update":
            fields = {}
            for k, v in [("title","TITLE"),("description","DESCRIPTION"),
                         ("responsible_id","RESPONSIBLE_ID"),("deadline","DEADLINE"),
                         ("group_id","GROUP_ID")]:
                if args.get(k): fields[v] = args[k]
            if args.get("priority") is not None: fields["PRIORITY"] = args["priority"]
            if args.get("status") is not None:   fields["STATUS"] = args["status"]
            if not fields: return "Ошибка: укажите хотя бы один параметр для обновления"
            r = await b24("tasks.task.update", {"taskId": args["task_id"], "fields": fields})
            return json.dumps(r.get("result", {}), ensure_ascii=False)

        elif name == "tasks_complete":
            r = await b24("tasks.task.complete", {"taskId": args["task_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "tasks_delete":
            r = await b24("tasks.task.delete", {"taskId": args["task_id"]})
            return json.dumps(r, ensure_ascii=False)

        elif name == "tasks_get_comments":
            r = await b24("task.commentitem.getlist", {"TASK_ID": args["task_id"]})
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "tasks_add_comment":
            r = await b24("task.commentitem.add", {
                "TASK_ID": args["task_id"],
                "FIELDS": {"POST_MESSAGE": args["comment"]}
            })
            return json.dumps(r, ensure_ascii=False)

        # ─── ЗВОНКИ ─────────────────────────────────────
        elif name == "telephony_get_calls":
            f = {}
            if args.get("date_from"):     f[">CALL_START_DATE"] = args["date_from"]
            if args.get("date_to"):       f["<CALL_START_DATE"] = args["date_to"]
            if args.get("user_id"):       f["PORTAL_USER_ID"] = args["user_id"]
            if args.get("call_type"):     f["CALL_TYPE"] = args["call_type"]
            if args.get("phone_number"):  f["PHONE_NUMBER"] = args["phone_number"]
            r = await b24("voximplant.statistic.get", {
                "filter": f,
                "select": ["ID","PORTAL_USER_ID","CALL_TYPE","CALL_DURATION","CALL_START_DATE",
                           "PHONE_NUMBER","PORTAL_NUMBER","CALL_FAILED_CODE","CRM_ENTITY_TYPE",
                           "CRM_ENTITY_ID","RECORD_FILE_ID","COST","CALL_VOTE"],
                "limit": args.get("limit", 50)
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "telephony_get_call":
            r = await b24("voximplant.statistic.get", {
                "filter": {"CALL_ID": args["call_id"]},
                "select": ["ID","PORTAL_USER_ID","CALL_TYPE","CALL_DURATION","CALL_START_DATE",
                           "PHONE_NUMBER","PORTAL_NUMBER","CALL_FAILED_CODE","CRM_ENTITY_TYPE",
                           "CRM_ENTITY_ID","RECORD_FILE_ID","COST","CALL_VOTE"]
            })
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        # ─── СОТРУДНИКИ ─────────────────────────────────
        elif name == "users_get":
            params = {"select": ["ID","NAME","LAST_NAME","EMAIL","WORK_PHONE","ACTIVE","DEPARTMENT"]}
            f = {}
            if args.get("active_only", True): f["ACTIVE"] = True
            if args.get("name"):           f["%NAME"] = args["name"]
            if args.get("last_name"):      f["%LAST_NAME"] = args["last_name"]
            if args.get("department_id"):  f["UF_DEPARTMENT"] = args["department_id"]
            if f: params["filter"] = f
            r = await b24("user.get", params)
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        elif name == "users_get_current":
            r = await b24("user.current", {})
            return json.dumps(r.get("result", {}), ensure_ascii=False, indent=2)

        elif name == "users_get_user":
            r = await b24("user.get", {"filter": {"ID": args["user_id"]},
                "select": ["ID","NAME","LAST_NAME","EMAIL","WORK_PHONE","ACTIVE","DEPARTMENT"]})
            results = r.get("result", [])
            return json.dumps(results[0] if results else {}, ensure_ascii=False, indent=2)

        # ─── ОТДЕЛЫ ─────────────────────────────────────
        elif name == "departments_get":
            params = {}
            if args.get("parent_id"): params["PARENT_ID"] = args["parent_id"]
            r = await b24("department.get", params)
            return json.dumps(r.get("result", []), ensure_ascii=False, indent=2)

        # ─── УВЕДОМЛЕНИЯ ────────────────────────────────
        elif name == "send_notification":
            r = await b24("im.message.add", {
                "DIALOG_ID": args["user_id"],
                "MESSAGE": args["message"]
            })
            return json.dumps(r, ensure_ascii=False)

        # ─── УНИВЕРСАЛЬНЫЙ ВЫЗОВ ────────────────────────
        elif name == "bitrix_call":
            r = await b24(args["method"], args.get("params", {}))
            return json.dumps(r, ensure_ascii=False, indent=2)

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
                "serverInfo": {"name": "bitrix24-mcp", "version": "3.0.0"}
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
    return {"status": "ok", "version": "3.0.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
