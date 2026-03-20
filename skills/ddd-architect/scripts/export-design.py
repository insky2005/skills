#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDD 设计导出工具 - 将设计文档落地为文件
让编程智能体 (Qwen Code/Cursor/Copilot) 可读可用的设计文档

用法:
    python export-design.py < input.json
    python export-design.py --output ./my-project < input.json
    python export-design.py --dry-run < input.json
    echo '{"strategic_design": {...}}' | python export-design.py
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

try:
    import yaml
except ImportError:
    print("❌ 错误：缺少 PyYAML 模块")
    print("请运行：pip install pyyaml")
    sys.exit(1)


# ============================================================================
# 常量定义
# ============================================================================

DEFAULT_EXPORT_ROOT = "./ddd-project"

PROJECT_STRUCTURE = [
    "docs/strategic",
    "docs/tactical",
    # "src/domain",
    # "src/application",
    # "src/infrastructure",
    # "src/interfaces",
]

TEMPLATE_FILES = {
    ".ddd-context": "ddd-context-template",
    "README.md": "readme-template",
    ".gitignore": "gitignore-template",
}


# ============================================================================
# 设计导出器
# ============================================================================

class DesignExporter:
    """DDD 设计文档导出器"""
    
    def __init__(self, export_root: str = DEFAULT_EXPORT_ROOT, verbose: bool = False):
        self.export_root = Path(export_root)
        self.verbose = verbose
        self.created_files: List[Dict[str, Any]] = []
        self.skipped_files: List[str] = []
    
    def log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"  {message}")
    
    def export(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        导出设计文档
        
        Args:
            design_data: 包含战略设计、战术设计等的字典
            
        Returns:
            导出结果字典
        """
        print(f"📦 开始导出设计文档到：{self.export_root}")
        print()
        
        # 1. 创建目录结构
        self._create_directories()
        
        # 2. 导出战略设计
        if design_data.get("strategic_design"):
            self._export_strategic_design(design_data["strategic_design"])
        
        # 3. 导出战术设计
        if design_data.get("tactical_designs"):
            self._export_tactical_designs(design_data["tactical_designs"])
        elif design_data.get("tactical_design"):
            # 支持单个战术设计
            context_name = design_data.get("context_name", "unknown")
            self._export_tactical_design(context_name, design_data["tactical_design"])
        
        # 4. 导出通用语言
        if design_data.get("ubiquitous_language"):
            self._export_ubiquitous_language(design_data["ubiquitous_language"])
        
        # 5. 生成编程智能体上下文文件（关键！）
        self._generate_agent_context(design_data)
        
        # 6. 生成 README
        self._generate_readme(design_data)
        
        # 7. 生成 .gitignore
        self._generate_gitignore()
        
        # 8. 生成导出报告
        result = self._generate_export_report(design_data)
        
        print()
        print(f"✅ 导出完成！共创建 {len(self.created_files)} 个文件")
        print(f"📁 导出位置：{self.export_root.resolve()}")
        
        return result
    
    def _create_directories(self):
        """创建标准目录结构"""
        print("📁 创建目录结构...")
        
        for dir_path in PROJECT_STRUCTURE:
            full_path = self.export_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Created: {dir_path}/")
        
        # 创建模板目录
        (self.export_root / "templates").mkdir(exist_ok=True)
        
        print(f"  ✅ 创建 {len(PROJECT_STRUCTURE)} 个目录")
    
    def _export_strategic_design(self, design: Dict[str, Any]):
        """导出战略设计"""
        print()
        print("📋 导出战略设计...")
        
        content = self._format_yaml({
            "@metadata": {
                "type": "strategic-design",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            },
            **design
        })
        
        self._write_file("docs/strategic/overview.yaml", content)
        
        # 同时生成 Markdown 版本（便于阅读）
        md_content = self._strategic_to_markdown(design)
        self._write_file("docs/strategic/overview.md", md_content)
    
    def _export_tactical_designs(self, designs: Dict[str, Dict[str, Any]]):
        """导出多个战术设计"""
        print()
        print("📋 导出战术设计...")
        
        for context_name, design in designs.items():
            self._export_tactical_design(context_name, design)
    
    def _export_tactical_design(self, context_name: str, design: Dict[str, Any]):
        """导出单个战术设计"""
        # YAML 版本（机器可读）
        content = self._format_yaml({
            "@metadata": {
                "type": "tactical-design",
                "context": context_name,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            },
            "context": context_name,
            **design
        })
        
        filename = f"{context_name.replace('-', '_')}.yaml"
        self._write_file(f"docs/tactical/{filename}", content)
        
        # Markdown 版本（人类可读）
        md_content = self._tactical_to_markdown(context_name, design)
        self._write_file(f"docs/tactical/{filename.replace('.yaml', '.md')}", md_content)
    
    def _export_ubiquitous_language(self, terms: List[Dict[str, Any]]):
        """导出通用语言"""
        print()
        print("📖 导出通用语言...")
        
        content = self._format_ubiquitous_language_md(terms)
        self._write_file("docs/ubiquitous-language.md", content)
        
        # 同时生成 YAML 版本
        yaml_content = self._format_yaml({
            "@metadata": {
                "type": "ubiquitous-language",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "terms": terms
        })
        self._write_file("docs/ubiquitous-language.yaml", yaml_content)
    
    def _generate_agent_context(self, design_data: Dict[str, Any]):
        """生成编程智能体上下文文件（关键！）"""
        print()
        print("🤖 生成编程智能体上下文文件...")
        
        # 提取基本信息
        project_name = design_data.get("project_name", "ddd-project")
        bounded_contexts = design_data.get("bounded_contexts", [])
        if not bounded_contexts and design_data.get("strategic_design"):
            bounded_contexts = design_data["strategic_design"].get("bounded_contexts", [])
        
        # 生成 .ddd-context 文件
        content = self._generate_ddd_context_content(project_name, bounded_contexts)
        self._write_file(".ddd-context", content)
        
        # 生成 .qwen/rules.md 文件 (Qwen Code 专用)
        qwen_rules = self._generate_qwen_rules(project_name, bounded_contexts)
        self._write_file(".qwen/rules.md", qwen_rules)
        
        # 生成 .cursorrules 文件（Cursor IDE 专用）
        cursor_rules = self._generate_cursor_rules(project_name, bounded_contexts)
        self._write_file(".cursorrules", cursor_rules)
        
        # 生成 .github/copilot-instructions.md（GitHub Copilot 专用）
        copilot_instructions = self._generate_copilot_instructions(project_name, bounded_contexts)
        self._write_file(".github/copilot-instructions.md", copilot_instructions)
    
    def _generate_readme(self, design_data: Dict[str, Any]):
        """生成项目 README"""
        print()
        print("📄 生成 README...")
        
        project_name = design_data.get("project_name", "DDD Project")
        bounded_contexts = design_data.get("bounded_contexts", [])
        if not bounded_contexts and design_data.get("strategic_design"):
            bounded_contexts = design_data["strategic_design"].get("bounded_contexts", [])
        
        content = self._generate_readme_content(project_name, bounded_contexts)
        self._write_file("README.md", content)
    
    def _generate_gitignore(self):
        """生成 .gitignore"""
        content = """# DDD Docs - Git Ignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Temporary
tmp/
temp/
*.tmp

# Design drafts (optional)
*.draft.yaml
*.wip.md
"""
        self._write_file(".gitignore", content)
    
    def _write_file(self, relative_path: str, content: str):
        """写入文件"""
        full_path = self.export_root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = len(content.encode('utf-8'))
        self.created_files.append({
            "path": relative_path,
            "full_path": str(full_path),
            "size": file_size,
            "size_human": self._format_size(file_size)
        })
        
        self.log(f"Created: {relative_path} ({self._format_size(file_size)})")
        print(f"  ✅ {relative_path}")
    
    def _format_yaml(self, data: Dict[str, Any]) -> str:
        """格式化 YAML"""
        return yaml.safe_dump(
            data,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            width=1000,
            indent=2
        )
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} GB"
    
    # =========================================================================
    # 内容生成方法
    # =========================================================================
    
    def _strategic_to_markdown(self, design: Dict[str, Any]) -> str:
        """战略设计转 Markdown"""
        lines = [
            "# 战略设计文档 (Strategic Design)",
            "",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]
        
        # 通用语言
        if design.get("ubiquitous_language"):
            lines.append("## 通用语言 (Ubiquitous Language)")
            lines.append("")
            for term in design["ubiquitous_language"]:
                lines.append(f"### {term.get('term', 'Unknown')}")
                lines.append(f"- **定义**: {term.get('definition', '')}")
                if term.get('example'):
                    lines.append(f"- **示例**: {term.get('example')}")
                lines.append("")
        
        # 子域划分
        if design.get("subdomains"):
            lines.append("## 子域划分 (Subdomains)")
            lines.append("")
            lines.append("| 子域 | 类型 | 说明 |")
            lines.append("|------|------|------|")
            for sub in design["subdomains"]:
                type_icon = {"core": "🎯", "supporting": "🔧", "generic": "📦"}.get(sub.get("type"), "•")
                lines.append(f"| {sub.get('name')} | {type_icon} {sub.get('type')} | {sub.get('rationale', '')} |")
            lines.append("")
        
        # 限界上下文
        if design.get("bounded_contexts"):
            lines.append("## 限界上下文 (Bounded Contexts)")
            lines.append("")
            for ctx in design["bounded_contexts"]:
                lines.append(f"### {ctx.get('name')}")
                lines.append(f"- **职责**: {ctx.get('responsibility', '')}")
                if ctx.get('candidate_aggregates'):
                    lines.append(f"- **候选聚合**: {', '.join(ctx['candidate_aggregates'])}")
                lines.append("")
        
        # 上下文映射
        if design.get("context_map"):
            lines.append("## 上下文映射 (Context Map)")
            lines.append("")
            lines.append("```mermaid")
            lines.append("graph TD")
            for mapping in design["context_map"]:
                upstream = mapping.get("upstream", "Unknown")
                downstream = mapping.get("downstream", "Unknown")
                pattern = mapping.get("pattern", "Unknown")
                lines.append(f"    {upstream} -- {pattern} --> {downstream}")
            lines.append("```")
            lines.append("")
        
        return "\n".join(lines)
    
    def _tactical_to_markdown(self, context_name: str, design: Dict[str, Any]) -> str:
        """战术设计转 Markdown"""
        lines = [
            f"# 战术设计：{context_name}",
            "",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]
        
        # 聚合设计
        if design.get("aggregates"):
            lines.append("## 聚合设计 (Aggregates)")
            lines.append("")
            
            for agg in design["aggregates"]:
                agg_name = agg.get("name", "Unknown")
                lines.append(f"### {agg_name}")
                lines.append("")
                
                # 聚合根
                if agg.get("root_entity"):
                    root = agg["root_entity"]
                    lines.append(f"**聚合根**: `{root.get('class', 'Unknown')}`")
                    if root.get("identity"):
                        lines.append(f"- ID 类型：{root.get('identity')}")
                    lines.append("")
                
                # 实体
                if agg.get("entities"):
                    lines.append("**实体**:")
                    for entity in agg["entities"]:
                        lines.append(f"- `{entity.get('class')}` (ID: {entity.get('identity', 'N/A')})")
                    lines.append("")
                
                # 值对象
                if agg.get("value_objects"):
                    lines.append("**值对象**:")
                    for vo in agg["value_objects"]:
                        attrs = vo.get("attributes", [])
                        immutable = "🔒 不可变" if vo.get("immutable") else "⚠️ 可变"
                        lines.append(f"- `{vo.get('class')}` [{immutable}] - {attrs}")
                    lines.append("")
                
                # 不变性规则
                if agg.get("invariants"):
                    lines.append("**不变性规则**:")
                    for inv in agg["invariants"]:
                        lines.append(f"- {inv.get('rule')} (由 `{inv.get('enforced_by')}` 执行)")
                    lines.append("")
                
                # 领域事件
                if agg.get("domain_events"):
                    lines.append("**领域事件**:")
                    for event in agg["domain_events"]:
                        lines.append(f"- `{event.get('name')}` - {event.get('trigger')}")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        # 应用服务
        if design.get("application_services"):
            lines.append("## 应用服务 (Application Services)")
            lines.append("")
            
            for svc in design["application_services"]:
                lines.append(f"### {svc.get('usecase', 'Unknown')}")
                lines.append(f"- **描述**: {svc.get('description', '')}")
                lines.append(f"- **触发角色**: {svc.get('actor', 'user')}")
                lines.append("")
                
                if svc.get("orchestration"):
                    lines.append("**流程**:")
                    for step in svc["orchestration"]:
                        lines.append(f"{step.get('step')}. {step.get('action')}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def _format_ubiquitous_language_md(self, terms: List[Dict[str, Any]]) -> str:
        """格式化通用语言为 Markdown"""
        lines = [
            "# 通用语言 (Ubiquitous Language)",
            "",
            f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "> 💡 这是团队统一的业务术语表，所有成员（包括开发、产品、业务）应使用相同的语言交流。",
            "",
            "---",
            "",
        ]
        
        for i, term in enumerate(terms, 1):
            lines.append(f"## {i}. {term.get('term', 'Unknown')}")
            lines.append("")
            lines.append(f"**定义**: {term.get('definition', '暂无定义')}")
            lines.append("")
            
            if term.get('example'):
                lines.append(f"**示例**:")
                lines.append(f"> {term.get('example')}")
                lines.append("")
            
            if term.get('related_terms'):
                lines.append(f"**相关术语**: {', '.join(term['related_terms'])}")
                lines.append("")
            
            if term.get('anti_pattern'):
                lines.append(f"**避免用法**: {term.get('anti_pattern')}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_ddd_context_content(self, project_name: str, bounded_contexts: List[Dict]) -> str:
        """生成 .ddd-context 文件内容"""
        ctx_list = "\n".join([
            f"  - name: {ctx.get('name', 'unknown')}\n"
            f"    responsibility: {ctx.get('responsibility', '')}\n"
            f"    design_file: docs/tactical/{ctx.get('name', 'unknown').replace('-', '_')}.yaml\n"
            # f"    src_path: src/{ctx.get('name', 'unknown').replace('-', '_')}/"
            for ctx in bounded_contexts
        ]) if bounded_contexts else "  # 暂无上下文定义"
        
        return f"""# DDD Design Context for AI Coding Assistant
# ================================================================================
# 编程智能体上下文文件 - 让 AI 理解设计意图
# 
# 使用方式:
#   - Qwen Code: 自动读取 .qwen/rules.md 和此文件
#   - Cursor: 自动读取 .cursorrules 和此文件
#   - GitHub Copilot: 参考 .github/copilot-instructions.md
# ================================================================================

project:
  name: {project_name}
  version: 1.0.0
  generated_at: {datetime.now(timezone.utc).isoformat()}
  design_tool: ddd-architect-skill

# ------------------------------------------------------------------------------
# 限界上下文清单
# ------------------------------------------------------------------------------
bounded_contexts:
{ctx_list}
# ------------------------------------------------------------------------------
# 编码规范 (必须遵守)
# ------------------------------------------------------------------------------
coding_rules:
  - "领域层 (domain/) 不得 import 基础设施层 (infrastructure/)"
  - "聚合根必须控制内部对象访问，外部不能直接引用聚合内实体"
  - "值对象所有字段必须 immutable (final/readonly)"
  - "跨上下文调用必须通过 ACL 或领域事件，禁止直接依赖"
  - "仓储接口定义在领域层，实现在基础设施层"
  - "领域方法命名使用业务语言，避免技术术语"
  - "一个事务只修改一个聚合"
  - "领域事件命名使用过去时 (OrderCreated, PaymentCompleted)"

# ------------------------------------------------------------------------------
# AI 编码指令
# ------------------------------------------------------------------------------
ai_instructions:
  - "编码前请先阅读对应的战术设计文件 @docs/tactical/{{context}}.yaml"
  - "生成代码时保持与设计文档的一致性"
  - "如发现设计与代码冲突，优先反馈设计问题而非强行编码"
  - "领域对象应包含业务行为，避免贫血模型 (只有 getter/setter)"
  - "为复杂业务逻辑编写单元测试，验证不变性规则"

# ------------------------------------------------------------------------------
# 文件位置索引
# ------------------------------------------------------------------------------
file_index:
  strategic_design: docs/strategic/overview.yaml
  strategic_design_md: docs/strategic/overview.md
  tactical_designs: docs/tactical/*.yaml
  ubiquitous_language: docs/ubiquitous-language.md

# ------------------------------------------------------------------------------
# 快速参考命令
# ------------------------------------------------------------------------------
quick_commands:
  validate_design: "python scripts/validate-aggregate.py < design.yaml"
  export_design: "python scripts/export-design.py < input.json"
  generate_skeleton: "python scripts/generate-skeleton.py --context order-context"
"""
    
    def _generate_qwen_rules(self, project_name: str, bounded_contexts: List[Dict]) -> str:
        """生成 .qwen/rules.md 文件 (Qwen Code 专用)"""
        return f"""# Rules for {project_name}
# DDD 项目编码规范

## 项目类型
DDD (Domain-Driven Design) 架构项目

## 核心原则
1. 领域驱动设计优先，技术实现其次
2. 保持领域层纯净，不依赖基础设施
3. 使用业务语言命名，避免技术术语

## 文件引用优先级
当用户请求编码时，按以下顺序查找设计文档:
1. .ddd-context (总体上下文)
2. docs/tactical/{{context}}.yaml (具体上下文战术设计)
3. docs/strategic/overview.yaml (战略设计)
4. docs/ubiquitous-language.md (通用语言)

## 代码生成规范
- 领域对象必须包含业务行为，拒绝贫血模型
- 值对象必须不可变
- 聚合根控制所有内部对象访问
- 跨上下文调用使用 ACL 或事件

## 禁止行为
- ❌ 在领域层 import 基础设施包
- ❌ 直接跨聚合修改状态
- ❌ 在实体中使用 setter 暴露内部状态
- ❌ 忽略设计文档直接生成代码
"""
    
    def _generate_cursor_rules(self, project_name: str, bounded_contexts: List[Dict]) -> str:
        """生成 .cursorrules 文件 (Cursor IDE 专用)"""
        return f"""# Cursor Rules for {project_name}
# DDD 项目编码规范

## 项目类型
DDD (Domain-Driven Design) 架构项目

## 核心原则
1. 领域驱动设计优先，技术实现其次
2. 保持领域层纯净，不依赖基础设施
3. 使用业务语言命名，避免技术术语

## 文件引用优先级
当用户请求编码时，按以下顺序查找设计文档:
1. .ddd-context (总体上下文)
2. docs/tactical/{{context}}.yaml (具体上下文战术设计)
3. docs/strategic/overview.yaml (战略设计)
4. docs/ubiquitous-language.md (通用语言)

## 代码生成规范
- 领域对象必须包含业务行为，拒绝贫血模型
- 值对象必须不可变
- 聚合根控制所有内部对象访问
- 跨上下文调用使用 ACL 或事件

## 禁止行为
- ❌ 在领域层 import 基础设施包
- ❌ 直接跨聚合修改状态
- ❌ 在实体中使用 setter 暴露内部状态
- ❌ 忽略设计文档直接生成代码
"""
    
    def _generate_copilot_instructions(self, project_name: str, bounded_contexts: List[Dict]) -> str:
        """生成 .github/copilot-instructions.md (GitHub Copilot 专用)"""
        ctx_names = ", ".join([ctx.get("name", "unknown") for ctx in bounded_contexts])
        
        return f"""# GitHub Copilot Instructions for {project_name}

## Project Overview
This is a Domain-Driven Design (DDD) project with the following bounded contexts: {ctx_names or "TBD"}

## Design Documentation
Before generating code, always check:
1. `.ddd-context` - Overall project context
2. `docs/tactical/*.yaml` - Tactical design for specific context
3. `docs/strategic/overview.yaml` - Strategic design
4. `docs/ubiquitous-language.md` - Business terminology

## Coding Standards

### Architecture
- Clean Architecture / Hexagonal Architecture
- Domain layer must NOT depend on infrastructure layer
- Repository interfaces in domain layer, implementations in infrastructure layer

### Domain Model
- Aggregates: Root entity controls access to internal entities
- Entities: Have identity and lifecycle
- Value Objects: Immutable, equality by value
- Domain Events: Named in past tense (OrderCreated, PaymentCompleted)

### Naming
- Use business language from ubiquitous language
- Avoid technical terms in domain layer
- Methods should express business intent

## Prohibited Patterns
- Anemic domain models (only getters/setters)
- Direct cross-aggregate state modification
- Infrastructure dependencies in domain layer
- Ignoring design documents when generating code

## When Asked to Generate Code
1. First, check if design document exists for the context
2. If design exists, follow it strictly
3. If design missing, ask user to clarify before generating
4. Always suggest validating design with validate-aggregate.py
"""
    
    def _generate_readme_content(self, project_name: str, bounded_contexts: List[Dict]) -> str:
        """生成 README.md"""
        ctx_table = "\n".join([
            f"| {ctx.get('name')} | {ctx.get('responsibility', 'N/A')} | `docs/tactical/{ctx.get('name', '').replace('-', '_')}.yaml` |"
            for ctx in bounded_contexts
        ]) if bounded_contexts else "| 暂无 | 暂无 | 暂无 |"
        
        return f"""# {project_name} - DDD Design Documentation

> 📋 本项目使用领域驱动设计 (DDD) 方法构建，设计文档由 DDD Architect Skill 生成。

## 📊 项目信息

| 项目 | 值 |
|------|-----|
| 项目名称 | {project_name} |
| 生成时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| 设计工具 | DDD Architect Skill v1.0 |
| 限界上下文 | {len(bounded_contexts)} 个 |

## 🗺️ 限界上下文

| 上下文 | 职责 | 设计文件 |
|--------|------|----------|
{ctx_table}

## 📁 目录结构

```
{self.export_root.name}/
├── .ddd-context              # 编程智能体上下文 (重要！)
├── .cursorrules              # Cursor IDE 规则
├── .qwen/
│   └── rules.md              # Qwen Code 规则
├── README.md                 # 本文档
└── docs/
    ├── strategic/
    │   ├── overview.yaml     # 战略设计 (机器可读)
    │   └── overview.md       # 战略设计 (人类可读)
    ├── tactical/
    │   ├── *.yaml            # 战术设计 (机器可读)
    │   └── *.md              # 战术设计 (人类可读)
    └── ubiquitous-language.md # 通用语言
```

## 🚀 快速开始

### 1. 阅读设计文档

```bash
# 查看战略设计
cat docs/strategic/overview.md

# 查看通用语言
cat docs/ubiquitous-language.md

# 查看特定上下文设计
cat docs/tactical/order_context.yaml
```

### 2. 编程智能体使用

在 Qwen Code / Cursor / Copilot 中:

```
@.ddd-context
@docs/tactical/order_context.yaml

请根据战术设计生成 Order 聚合根代码
```

### 3. 设计校验

```bash
# 校验聚合设计
cat docs/tactical/order_context.yaml | python scripts/validate-aggregate.py
```

## 🤖 AI 编码指南

### 推荐工作流

1. **阅读设计** → 先理解 `docs/tactical/{{context}}.yaml`
2. **生成代码** → 基于设计生成骨架代码
3. **校验设计** → 运行 `validate-aggregate.py` 确保合规
4. **迭代优化** → 根据反馈调整设计或代码

### 设计优先原则

- ✅ 设计文档是代码的"单一事实来源"
- ✅ 代码变更应先更新设计文档
- ✅ 设计与代码冲突时，优先讨论设计问题

## 📚 参考资源

- [DDD Architect Skill](https://github.com/your-org/ddd-architect)
- [Domain-Driven Design Reference](https://domainlanguage.com/ddd/)
- [Aggregate Design Guidelines](https://martinfowler.com/bliki/DDD_Aggregate.html)

## 📄 许可证

详见 LICENSE（若无，请忽略）
"""
    
    def _generate_export_report(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成导出报告"""
        return {
            "success": True,
            "export_root": str(self.export_root.resolve()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project_name": design_data.get("project_name", "unknown"),
            "files": self.created_files,
            "files_count": len(self.created_files),
            "total_size": sum(f["size"] for f in self.created_files),
            "structure": {
                "docs/strategic": len([f for f in self.created_files if "strategic" in f["path"]]),
                "docs/tactical": len([f for f in self.created_files if "tactical" in f["path"]]),
                # "src": len([f for f in self.created_files if "src/" in f["path"]]),
                "other": len([f for f in self.created_files if "strategic" not in f["path"] and "tactical" not in f["path"] and "src/" not in f["path"]])
            }
        }


# ============================================================================
# 主入口
# ============================================================================

def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="DDD 设计导出工具 - 将设计文档落地为文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从 stdin 读取设计数据
  echo '{"strategic_design": {...}}' | python export-design.py
  
  # 指定输出目录
  cat design.json | python export-design.py --output ./my-project
  
  # 预览模式 (不实际写入)
  cat design.json | python export-design.py --dry-run
  
  # 详细输出
  cat design.json | python export-design.py --verbose
        """
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=DEFAULT_EXPORT_ROOT,
        help=f"输出目录 (默认：{DEFAULT_EXPORT_ROOT})"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式，不实际写入文件"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式报告"
    )
    
    args = parser.parse_args()
    
    # 读取 stdin 输入
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print("❌ 错误：stdin 为空", file=sys.stderr)
            print("用法：cat design.json | python export-design.py", file=sys.stderr)
            sys.exit(1)
        design_data = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误：{e}", file=sys.stderr)
        sys.exit(1)
    
    # 导出
    exporter = DesignExporter(export_root=args.output, verbose=args.verbose)
    
    if args.dry_run:
        print("🔍 Dry Run 模式 - 不实际写入文件")
        print()
        result = {
            "success": True,
            "dry_run": True,
            "export_root": args.output,
            "message": "预览模式完成，未创建任何文件"
        }
    else:
        result = exporter.export(design_data)
    
    # 输出报告
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print()
        print("=" * 60)
        print("📊 导出报告")
        print("=" * 60)
        print(f"项目：{result.get('project_name', 'unknown')}")
        print(f"文件数：{result.get('files_count', 0)}")
        print(f"总大小：{exporter._format_size(result.get('total_size', 0))}")
        print(f"位置：{result.get('export_root')}")
        print()
        print("创建的文件:")
        for f in result.get("files", []):
            print(f"  ✅ {f['path']} ({f['size_human']})")


if __name__ == "__main__":
    main()