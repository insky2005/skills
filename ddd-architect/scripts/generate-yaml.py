#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML 输出格式化工具 - 确保符合 agentskills.io 规范
用法：python generate-yaml.py <mode> < input.json
"""

import yaml
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any


def format_output(data: Dict[str, Any], mode: str) -> str:
    """格式化输出为指定模式"""
    output = {
        "@metadata": {
            "skill": "ddd-architect",
            "mode": mode,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": "1.0.0"
        },
        **data
    }
    
    return yaml.safe_dump(
        output,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=1000
    )


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("用法：python generate-yaml.py <mode> < input.json", file=sys.stderr)
        print("mode: strategic | tactical | review", file=sys.stderr)
        sys.exit(1)
    
    mode = sys.argv[1]
    valid_modes = ["strategic", "tactical", "review"]
    
    if mode not in valid_modes:
        print(f"错误：mode 必须是 {valid_modes} 之一", file=sys.stderr)
        sys.exit(1)
    
    try:
        input_data = json.load(sys.stdin)
        output = format_output(input_data, mode)
        print(f"# @output: {mode}-design")
        print(output)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误：{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"处理错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()