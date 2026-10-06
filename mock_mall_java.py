#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java mall 后端模拟器（Stage 6 闭环演示用，端口 8085）
实现 FastAPI 服务所需的接口：
  POST /sso/login                                   → token
  GET  /sso/info                                    → member
  GET  /order/ai/detail/by-sn/{sn}                  → 订单快照（三文鱼订单）
  GET/POST /ai/conversations/...                    → 会话历史
  POST /after-sales/ai/eligibility                  → 售后资格核验
  POST /after-sales/ai/applications                 → 可信写入（写权威模拟）
  GET  /after-sales/ai/submissions/{idempotency_key} → 幂等提交核实
生产环境应替换为真实 Java mall-portal/mall-admin（Docker 启动）。
"""
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Mock Java Mall API")

DEMO_USER = {"username": "salmon_user", "password": "salmon123"}
TOKENS = {"mock-token-salmon-001": 1001}

ORDERS = {
    "20260922001": {
        "orderSn": "20260922001",
        "status": 3,
        "statusText": "已签收",
        "deliveryCompany": "顺丰冷链速运",
        "deliverySn": "SF3188992200066",
        "productNames": ["挪威冰鲜三文鱼刺身 400g"],
        "orderItems": [
            {
                "orderItemId": 88001,
                "productName": "挪威冰鲜三文鱼刺身 400g",
                "productAttr": "400g 刺身级 中段",
                "productQuantity": 1,
            }
        ],
    }
}


@app.post("/sso/login")
async def sso_login(request: Request):
    form = await request.form()
    if (form.get("username"), form.get("password")) == (DEMO_USER["username"], DEMO_USER["password"]):
        return JSONResponse({"code": 200, "message": "OK",
                             "data": {"token": "mock-token-salmon-001", "tokenHead": "Bearer"}})
    return JSONResponse({"code": 401, "message": "用户名或密码错误"}, status_code=401)


@app.get("/sso/info")
def sso_info(authorization: str = Header(default=None)):
    token = (authorization or "").replace("Bearer ", "").strip()
    if token in TOKENS:
        return JSONResponse({"code": 200, "message": "OK", "data": {"id": TOKENS[token], "username": DEMO_USER["username"]}})
    return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)


@app.get("/order/ai/detail/by-sn/{order_sn}")
def order_detail(order_sn: str, authorization: str = Header(default=None)):
    token = (authorization or "").replace("Bearer ", "").strip()
    if token not in TOKENS:
        return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)
    order = ORDERS.get(order_sn)
    if order is None:
        return JSONResponse({"code": 404, "message": "订单不存在或无权访问"}, status_code=200)
    return JSONResponse({"code": 200, "message": "OK", "data": order})


@app.get("/ai/conversations/{conversation_id}")
def get_conversation(conversation_id: str, authorization: str = Header(default=None)):
    token = (authorization or "").replace("Bearer ", "").strip()
    if token not in TOKENS:
        return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)
    return JSONResponse({
        "code": 200, "message": "OK",
        "data": {
            "conversation": {
                "conversationId": conversation_id,
                "title": "会话",
                "messageCount": 0,
                "createdAt": "2026-10-06T14:00:00",
                "updatedAt": "2026-10-06T14:00:00",
            },
            "messages": [],
        },
    })


@app.post("/ai/conversations/{conversation_id}/transcript")
async def append_transcript(conversation_id: str, request: Request, authorization: str = Header(default=None)):
    token = (authorization or "").replace("Bearer ", "").strip()
    if token not in TOKENS:
        return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)
    return JSONResponse({"code": 200, "message": "OK", "data": None})


@app.post("/after-sales/ai/eligibility")
async def after_sales_eligibility(request: Request, authorization: str = Header(default=None)):
    token = (authorization or "").replace("Bearer ", "").strip()
    if token not in TOKENS:
        return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)
    body = await request.json()
    order_sn = body.get("orderSn", "")
    app_type = body.get("applicationType", "return_refund")
    labels = {"return_refund": "退货退款", "exchange": "换货", "refund": "仅退款"}
    return JSONResponse({
        "code": 200, "message": "OK",
        "data": {
            "orderSn": order_sn,
            "applicationType": app_type,
            "applicationTypeLabel": labels.get(app_type, "退货退款"),
            "orderStatus": "已签收",
            "eligible": True,
            "requiresProductSelection": False,
            "decision": "eligible_to_apply",
            "message": "订单已签收，可发起售后申请；最终结果以售后审核为准。",
            "productName": "挪威冰鲜三文鱼刺身 400g",
            "productAttr": "400g 刺身级 中段",
        },
    })


@app.post("/after-sales/ai/applications")
async def create_application(request: Request, authorization: str = Header(default=None)):
    """可信写入演示：Java 是唯一写权威，接收 Agent 促成的申请提交。"""
    token = (authorization or "").replace("Bearer ", "").strip()
    if token not in TOKENS:
        return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)
    body = await request.json()
    labels = {"return_refund": "退货退款", "exchange": "换货", "refund": "仅退款"}
    import time
    now = int(time.time() * 1000)
    return JSONResponse({
        "code": 200, "message": "OK",
        "data": {
            "applicationId": 90001,
            "orderSn": body.get("orderSn", ""),
            "applicationType": body.get("applicationType", "exchange"),
            "applicationTypeLabel": labels.get(body.get("applicationType", ""), "换货"),
            "productName": "挪威冰鲜三文鱼刺身 400g",
            "productAttr": "400g 刺身级 中段",
            "reason": body.get("reason", ""),
            "description": body.get("description", ""),
            "status": "pending_review",
            "statusLabel": "待审核",
            "canCancel": False,
            "canModify": False,
            "createdAt": now,
            "updatedAt": now,
        },
    })


@app.get("/after-sales/ai/submissions/{idempotency_key}")
def get_submission(idempotency_key: str, authorization: str = Header(default=None)):
    """幂等提交状态查询：返回同一份申请视图，实现可信确认闭环。"""
    token = (authorization or "").replace("Bearer ", "").strip()
    if token not in TOKENS:
        return JSONResponse({"code": 401, "message": "token 无效"}, status_code=401)
    import time
    now = int(time.time() * 1000)
    return JSONResponse({
        "code": 200, "message": "OK",
        "data": {
            "status": "created",
            "application": {
                "applicationId": 90001,
                "orderSn": "20260922001",
                "applicationType": "exchange",
                "applicationTypeLabel": "换货",
                "productName": "挪威冰鲜三文鱼刺身 400g",
                "productAttr": "400g 刺身级 中段",
                "reason": "商品存在质量问题",
                "description": "商品存在质量问题",
                "status": "pending_review",
                "statusLabel": "待审核",
                "canCancel": False,
                "canModify": False,
                "createdAt": now,
                "updatedAt": now,
            },
        },
    })


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8085)
