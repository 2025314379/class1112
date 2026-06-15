"""外部工具调用模块 —— Skill 3
模拟三个外部 API：修改地址、物流查询、库存查询
"""
import random
from datetime import datetime, timedelta


# ---------- 工具定义（OpenAI Function Calling 格式）----------

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "update_shipping_address",
            "description": "修改订单的收货地址。仅未发货订单可修改。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "订单号，如 ORD20240601001",
                    },
                    "new_address": {
                        "type": "string",
                        "description": "新的收货地址，需包含省市区和详细地址",
                    },
                },
                "required": ["order_id", "new_address"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_express_info",
            "description": "根据订单号查询物流信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "订单号，如 ORD20240601001",
                    },
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_product_stock",
            "description": "查询指定商品的当前库存状态",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "商品名称或 SKU 编码",
                    },
                },
                "required": ["product_name"],
            },
        },
    },
]


# ---------- 工具实现 ----------

# 模拟物流公司
EXPRESS_COMPANIES = ["中通快递", "圆通速递", "顺丰速运", "韵达快递", "申通快递"]
# 模拟物流状态
EXPRESS_STATUSES = ["运输中", "已揽收", "到达中转站", "派送中", "已签收", "待揽收"]


def update_shipping_address(order_id: str, new_address: str) -> dict:
    """模拟修改收货地址"""
    # 模拟：部分订单已发货不可修改
    if order_id.endswith("9"):
        return {
            "success": False,
            "message": f"订单 {order_id} 已发货，无法修改地址。建议您联系快递员或拒收后重新下单。",
        }
    return {
        "success": True,
        "message": f"订单 {order_id} 的收货地址已成功修改为：{new_address}",
        "order_id": order_id,
        "new_address": new_address,
    }


def get_express_info(order_id: str) -> dict:
    """模拟查询物流信息"""
    if not order_id or len(order_id) < 6:
        return {
            "success": False,
            "message": "订单号格式不正确，请核实后重新提供。",
        }

    company = random.choice(EXPRESS_COMPANIES)
    status = random.choice(EXPRESS_STATUSES)
    now = datetime.now()

    # 生成模拟物流轨迹
    traces = []
    base_time = now - timedelta(days=random.randint(1, 5))
    for i in range(random.randint(2, 5)):
        trace_time = base_time + timedelta(hours=random.randint(2, 24))
        cities = ["上海", "杭州", "北京", "广州", "深圳", "成都", "武汉"]
        city = random.choice(cities)
        actions = ["已揽收", "到达分拣中心", "运输中", "到达网点", "派送中", "已签收"]
        traces.append({
            "time": trace_time.strftime("%Y-%m-%d %H:%M:%S"),
            "location": city,
            "status": actions[min(i, len(actions) - 1)],
        })

    return {
        "success": True,
        "order_id": order_id,
        "express_company": company,
        "express_number": f"EXP{random.randint(10000000000, 99999999999)}",
        "status": status,
        "estimated_delivery": (now + timedelta(days=random.randint(1, 3))).strftime("%Y-%m-%d"),
        "traces": traces,
    }


def check_product_stock(product_name: str) -> dict:
    """模拟查询商品库存"""
    # 模拟一些商品的库存数据
    mock_stock = {
        "iPhone": {"stock": 128, "warehouse": "上海仓"},
        "华为": {"stock": 56, "warehouse": "深圳仓"},
        "小米": {"stock": 0, "warehouse": "北京仓"},  # 缺货示例
        "耐克": {"stock": 200, "warehouse": "广州仓"},
        "阿迪达斯": {"stock": 89, "warehouse": "上海仓"},
        "SKU": {"stock": 42, "warehouse": "成都仓"},
    }

    # 匹配商品
    matched = None
    for key, val in mock_stock.items():
        if key.lower() in product_name.lower():
            matched = val
            break

    if matched is None:
        return {
            "success": True,
            "product_name": product_name,
            "stock": random.randint(0, 150),
            "warehouse": random.choice(["上海仓", "深圳仓", "北京仓", "广州仓"]),
            "status": "有货" if random.random() > 0.2 else "库存紧张",
        }

    status = "缺货" if matched["stock"] == 0 else ("库存紧张" if matched["stock"] < 60 else "有货")
    return {
        "success": True,
        "product_name": product_name,
        "stock": matched["stock"],
        "warehouse": matched["warehouse"],
        "status": status,
    }


# 工具名称到函数的映射
TOOL_FUNCTIONS = {
    "update_shipping_address": update_shipping_address,
    "get_express_info": get_express_info,
    "check_product_stock": check_product_stock,
}
