#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚合设计校验工具 - 检查常见 DDD 反模式
用法：python validate-aggregate.py < design.yaml
"""

# 友好的依赖检查
try:
    import yaml
except ImportError:
    print("❌ 错误：缺少 PyYAML 模块")
    print()
    print("请运行以下命令安装:")
    print("   pip install pyyaml")
    print()
    import sys
    sys.exit(1)

import sys
import json
from typing import Dict, List, Any, Optional


class AggregateValidator:
    """聚合设计校验器"""
    
    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.suggestions: List[str] = []
    
    def validate(self, design_yaml: str) -> Dict[str, Any]:
        """校验聚合设计"""
        try:
            design = yaml.safe_load(design_yaml)
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "error": f"YAML 解析失败：{str(e)}",
                "issues": [],
                "suggestions": []
            }
        
        self.issues = []
        self.suggestions = []
        
        # 检查 aggregates 是否存在
        aggregates = design.get("aggregates", [])
        if not aggregates:
            self.issues.append({
                "code": "MISSING_AGGREGATES",
                "message": "未定义任何聚合",
                "severity": "error"
            })
            self.suggestions.append("至少定义一个聚合根作为设计起点")
        
        for agg in aggregates:
            self._validate_aggregate(agg)
        
        return {
            "valid": len([i for i in self.issues if i["severity"] == "error"]) == 0,
            "aggregate_name": design.get("context", "unknown"),
            "issues_count": len(self.issues),
            "issues": self.issues,
            "suggestions": self.suggestions
        }
    
    def _validate_aggregate(self, agg: Dict[str, Any]) -> None:
        """校验单个聚合"""
        agg_name = agg.get("name", "Unknown")
        
        # 检查 1: 聚合根是否定义
        if not agg.get("root_entity"):
            self.issues.append({
                "code": "MISSING_ROOT",
                "aggregate": agg_name,
                "message": "未定义聚合根",
                "severity": "error"
            })
            self.suggestions.append(f"为 {agg_name} 添加 root_entity 字段")
        
        # 检查 2: 值对象是否标记不可变
        for vo in agg.get("value_objects", []):
            if not vo.get("immutable", False):
                self.issues.append({
                    "code": "VO_MUTABLE",
                    "aggregate": agg_name,
                    "message": f"值对象 {vo.get('class')} 未标记 immutable",
                    "severity": "warning"
                })
                self.suggestions.append(f"为值对象 {vo.get('class')} 添加 immutable: true")
        
        # 检查 3: 不变性规则是否有执行方法
        for inv in agg.get("invariants", []):
            if "enforced_by" not in inv:
                self.issues.append({
                    "code": "INVARIANT_NO_ENFORCER",
                    "aggregate": agg_name,
                    "message": f"不变性规则未指定执行方法：{inv.get('rule', '未知')}",
                    "severity": "warning"
                })
                self.suggestions.append("在 enforced_by 字段指定负责校验的领域方法名")
        
        # 检查 4: 领域事件命名规范
        for event in agg.get("domain_events", []):
            event_name = event.get("name", "")
            if event_name and not (event_name.endswith("ed") or event_name.endswith("ing")):
                self.issues.append({
                    "code": "EVENT_NAMING",
                    "aggregate": agg_name,
                    "message": f"事件 {event_name} 建议使用过去时命名",
                    "severity": "info"
                })
                self.suggestions.append(f"将事件重命名为 {event_name}ed 或 {event_name}Completed")
    
    def format_report(self, result: Dict[str, Any]) -> str:
        """格式化校验报告"""
        if result.get("error"):
            return f"❌ 校验错误：{result['error']}"
        
        lines = ["## 聚合设计校验报告", ""]
        lines.append(f"**上下文**: {result.get('aggregate_name', 'unknown')}")
        
        status = "✅ 通过" if result["valid"] else f"⚠️ 发现 {result['issues_count']} 个问题"
        lines.append(f"**状态**: {status}")
        lines.append("")
        
        if result["issues"]:
            lines.append("### 🔍 发现问题")
            for i, issue in enumerate(result["issues"], 1):
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.get("severity"), "•")
                lines.append(f"{i}. {severity_icon} [{issue.get('code')}] {issue.get('message')}")
            lines.append("")
            
            lines.append("### 💡 改进建议")
            for i, suggestion in enumerate(result["suggestions"], 1):
                lines.append(f"{i}. {suggestion}")
        
        # 使用实际换行符连接
        return "\n".join(lines)


def main():
    """主入口"""
    validator = AggregateValidator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("用法：python validate-aggregate.py < design.yaml")
        print("      或：echo '$YAML' | python validate-aggregate.py")
        print("")
        print("选项:")
        print("  --json    输出 JSON 格式")
        print("  --help    显示帮助信息")
        sys.exit(0)
    
    input_yaml = sys.stdin.read()
    result = validator.validate(input_yaml)
    
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(validator.format_report(result))


if __name__ == "__main__":
    main()