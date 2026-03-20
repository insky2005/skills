# DDD 模式速查手册

## 🎯 战略设计模式

### 子域类型决策树

```
业务价值高？──否──> Generic Domain (外购/开源)
   │
  是
   │
技术差异化？──否──> Supporting Domain (自研但可标准化)
   │
  是
   │
   └──> Core Domain (核心竞争力，持续投入)
```

### 子域类型对比

| 类型 | 英文 | 特点 | 投入策略 | 示例 |
|------|------|------|---------|------|
| 核心域 | Core Domain | 业务核心竞争力 | 最高优先级，持续投入 | 风控引擎、推荐算法 |
| 支撑域 | Supporting Domain | 业务必需但非核心 | 中等投入，可标准化 | 库存管理、订单处理 |
| 通用域 | Generic Domain | 市场有成熟方案 | 最低投入，外购/开源 | 身份认证、消息推送 |

---

## 🔧 战术设计模式

### 聚合设计原则

```yaml
# ✅ 好的聚合特征
aggregate:
  size: "建议 ≤ 5 个实体/值对象"
  consistency: "聚合内强一致，聚合间最终一致"
  access: "外部只能通过聚合根访问"
  transaction: "一个事务只修改一个聚合"

# ❌ 常见反模式
anti_patterns:
  - "上帝聚合：承担过多职责，难以维护"
  - "大对象图：加载聚合时牵一发而动全身"
  - "跨聚合事务：试图用数据库事务保证多个聚合一致"
```

### 值对象设计清单

```markdown
- [ ] 无唯一标识，基于属性值判断相等
- [ ] 所有字段 immutable (final/readonly)
- [ ] 重写 equals() 和 hashCode()
- [ ] 封装相关校验逻辑
- [ ] 提供工厂方法或静态构造器
```

### 领域事件命名规范

```
# 格式：<Aggregate><StateChange>ed
# 时态：过去时，表示已发生的事实

✅ OrderCreated      ✅ PaymentCompleted    ✅ InventoryReserved
❌ CreateOrder       ❌ CompletePayment     ❌ ReserveInventory
```

---

## 🧪 测试策略

### 领域层测试 (单元测试)

```python
# 测试重点：不变性规则 + 领域行为
def test_order_cancel_after_paid():
    order = Order.create(...)
    order.mark_paid()
    
    with pytest.raises(BusinessRuleViolation):
        order.cancel()  # 违反"已支付不可取消"规则
```

### 应用层测试 (集成测试)

```python
# 测试重点：用例流程 + 事务边界 + 事件发布
def test_create_order_flow():
    cmd = CreateOrderCmd(user_id="u1", items=[...])
    result = order_service.create_order(cmd)
    
    assert result.order_id is not None
    assert event_publisher.has_published(OrderCreated)
```