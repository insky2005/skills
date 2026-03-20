# 战术构建块参考手册

## 🧱 核心构建块对比

| 构建块 | 唯一标识 | 可变性 | 相等性判断 | 典型用途 |
|--------|---------|--------|-----------|---------|
| Entity (实体) | ✅ ID | ✅ 可变 | ID 相等 | 有生命周期的业务对象 |
| ValueObject (值对象) | ❌ 无 | ❌ 不可变 | 属性值相等 | 描述特征/度量/参数 |
| AggregateRoot (聚合根) | ✅ ID | ✅ 可变 | ID 相等 | 事务边界，封装不变性 |
| DomainEvent (领域事件) | ❌ 无 | ❌ 不可变 | (通常不需比较) | 记录已发生的业务事实 |
| DomainService (领域服务) | ❌ 无 | - | - | 跨实体的业务逻辑 |
| Repository (仓储) | ❌ 无 | - | - | 聚合的持久化抽象 |

---

## 🎯 聚合设计自检清单

```yaml
aggregate_checklist:
  boundary:
    - "聚合根是否控制所有内部对象的访问？"
    - "外部引用是否只通过聚合根 ID？"
    - "聚合大小是否可控 (建议 ≤ 5 个实体)？"
  
  consistency:
    - "聚合内不变性规则是否明确定义？"
    - "业务规则是否封装在领域方法中？"
    - "状态变更是否通过领域方法触发？"
  
  persistence:
    - "仓储接口是否定义在领域层？"
    - "仓储实现是否在基础设施层？"
    - "是否避免在领域方法中直接调用 ORM？"
  
  events:
    - "状态变更是否发布对应的领域事件？"
    - "事件命名是否使用过去时？"
    - "事件 payload 是否只包含必要快照数据？"
```

---

## 💰 值对象设计示例

```python
# Python 示例：Money 值对象
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("金额不能为负数")
    
    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise CurrencyMismatchError(...)
        return Money(self.amount + other.amount, self.currency)
```

```java
// Java 示例：Address 值对象
@Value
public class Address {
    String province;
    String city;
    String district;
    String detail;
    
    public String toFullString() {
        return String.format("%s%s%s%s", province, city, district, detail);
    }
}
```