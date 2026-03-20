# 上下文映射决策指南

## 🔍 集成模式选择决策树

```
需要实时同步数据？
├─ 是 → 调用方性能要求高？
│   ├─ 是 → OHS (Open Host Service) + 缓存
│   └─ 否 → ACL (防腐层) + 同步调用
│
└─ 否 → 业务允许异步？
    ├─ 是 → Event-Driven (事件驱动)
    │
    └─ 否 → 数据共享需求强？
        ├─ 是 → SharedKernel (共享内核)
        │
        └─ 否 → Conformist (遵奉者) / Separate Ways
```

## 📋 各模式实施检查清单

### ACL (防腐层)

```yaml
required:
  - 定义下游接口的 Adapter 接口 (领域层)
  - 实现基础设施层的 AdapterImpl
  - 转换：外部模型 → 领域模型 (入向)
  - 转换：领域模型 → 外部模型 (出向)
  
avoid:
  - 领域层直接 import 外部 SDK
  - 在应用层做模型转换
  
test:
  - Adapter 单元测试：验证转换逻辑
  - 契约测试：确保下游接口变更时及时感知
```

### Event-Driven (事件驱动)

```yaml
required:
  - 事件 Schema 注册到 Schema Registry
  - 事件命名使用过去时 (OrderPaid)
  - 消费者实现幂等处理
  - 关键事件持久化 (Outbox 表)
  
avoid:
  - 事件 payload 包含冗余数据
  - 消费者直接修改生产者数据库
  - 忽略事件顺序要求
  
test:
  - 事件契约测试：Schema 变更兼容性
  - 幂等测试：重复消费不产生副作用
```

### SharedKernel (共享内核)

```yaml
required:
  - 共享代码独立版本管理
  - 变更通知机制 (Changelog)
  - 共享模型明确标注 @Shared
  
avoid:
  - 隐式共享：通过传递依赖引入
  - 双向依赖
  - 过度共享
  
test:
  - 共享库独立测试套件
  - 各上下文集成测试验证兼容性
```

## 🚨 常见陷阱

| 陷阱 | 现象 | 规避方案 |
|------|------|---------|
| 隐式耦合 | 修改 A 上下文导致 B 编译失败 | 显式声明依赖 + 契约测试 |
| 事件泛滥 | 每个状态变更都发事件 | 只发布关键业务事件 |
| 共享库膨胀 | SharedKernel 包含过多逻辑 | 定期评审，移出不稳定逻辑 |