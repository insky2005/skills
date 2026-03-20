# DDD Architect Skill

基于 [agentskills.io](https://agentskills.io/specification) 规范构建的领域驱动设计专家助手。

## 📦 版本信息

- **版本**: {SKILL_VERSION}
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **许可证**: MIT

## 🚀 快速开始

### 1. 部署技能包

```bash
# 方式 A: 直接上传目录 (推荐)
将 ddd-architect/ 目录上传至支持 agentskills.io 的平台

# 方式 B: 打包上传
cd ddd-architect && zip -r ddd-architect-v{SKILL_VERSION}.zip .
```

### 2. 激活技能

在 Agent 配置中启用 `ddd-architect` 技能，或在 System Prompt 中添加:

```
You have access to the ddd-architect skill. 
Use /strategic for business analysis, /tactical for domain modeling, /check for design review.
```

### 3. 开始使用

```bash
# 战略设计：分析业务边界
/strategic 电商系统，包含用户、商品、订单、支付、库存

# 战术设计：细化某个上下文
/tactical order-context

# 设计评审：检查现有设计
/check <粘贴你的聚合设计 YAML>

# 加载参考资源
/load ddd-patterns

# 使用模板
/template tactical
```

## 📚 核心能力

### 战略设计 (Strategic)
- ✅ 子域识别与划分 (Core/Supporting/Generic)
- ✅ 限界上下文定义与职责边界
- ✅ 上下文映射模式推荐 (ACL/Event/SharedKernel...)
- ✅ 通用语言 (Ubiquitous Language) 提取

### 战术设计 (Tactical)
- ✅ 聚合根/实体/值对象建模
- ✅ 不变性规则 (Invariants) 定义与校验
- ✅ 领域事件设计与发布策略
- ✅ 应用服务用例编排

### 设计评审 (Review)
- ✅ 贫血模型检测
- ✅ 聚合边界合理性评估
- ✅ 依赖方向合规检查
- ✅ 改进建议与重构方案

## 🔧 高级用法

### 迭代式设计流程

```bash
# Step 1: 粗粒度战略设计
/strategic <业务描述>

# Step 2: 确认上下文后细化
/tactical order-context

# Step 3: 校验聚合设计
python scripts/validate-aggregate.py < design.yaml

# Step 4: 生成代码结构建议 (需确认设计后)
/code-structure java
```

### 模糊业务规则澄清

当业务规则不明确时，技能会主动反问:

```
❓ 库存不足时订单策略？
A) 直接失败  B) 等待补货  C) 部分发货  D) 拆单
请选择或补充业务规则...
```

### 输出格式控制

```bash
/simplify      # 仅输出核心要素 (节省 Token)
/export md     # 输出标准 Markdown 文档
/export json   # 输出 JSON 格式便于程序处理
```

## 🛡️ 防护规则

技能内置以下 Guardrails，确保 DDD 实践质量:

```yaml
guardrails:
  - "领域层不得依赖基础设施层 (依赖倒置)"
  - "聚合根必须控制内部对象访问 (封装不变性)"
  - "值对象必须标记 immutable (防御式编程)"
  - "跨上下文调用必须经过 ACL 或事件 (解耦)"
  - "拒绝直接生成业务代码，先确认领域模型"
  - "模糊业务规则必须反问澄清，不得臆造"
```

## 📁 文件结构

```
ddd-architect/
├── SKILL.md                     # [必需] 技能元数据 + 核心指令
├── README.md                    # 本文档
├── LICENSE                      # MIT 许可证
├── scripts/
│   ├── validate-aggregate.py    # 聚合设计校验工具
│   └── generate-yaml.py         # YAML 输出格式化
├── references/
│   ├── ddd-patterns.md          # DDD 模式速查
│   ├── context-map-patterns.md  # 上下文映射指南
│   └── tactical-building-blocks.md  # 战术构建块参考
└── assets/
    ├── templates/
    │   ├── strategic-design.yaml
    │   ├── tactical-design.yaml
    │   └── review-checklist.yaml
    └── diagrams/
        └── aggregate-lifecycle.mmd
```

## 🤝 贡献指南

1. **新增模式参考** → 添加到 `references/` 并更新 `SKILL.md` 的 `/load` 命令
2. **优化输出模板** → 修改 `assets/templates/` 并测试格式化
3. **新增校验规则** → 扩展 `scripts/validate-aggregate.py`

## 📄 许可证

MIT License - 自由使用、修改、分发