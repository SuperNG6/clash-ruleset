import yaml
import os
from datetime import datetime

# 定义规则文件路径
rule_files = ['rules/Gemini.yaml', 'rules/OpenAI.yaml', 'rules/Claude.yaml']

# 初始化统计信息
stats = {
    'DOMAIN': 0,
    'DOMAIN-KEYWORD': 0,
    'DOMAIN-SUFFIX': 0,
    'IP-ASN': 0,
    'IP-CIDR': 0,
    'TOTAL': 0
}

# 用于存储合并后的规则
merged_rules = set()

# 用于存储来源信息
sources = []

for file in rule_files:
    with open(file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        # 假设元数据在文件顶部的注释中，这里需要根据实际情况调整
        # 如果元数据在 YAML 的特定字段中，可以直接读取
        # 这里假设每个文件有一个 'metadata' 字段包含相关信息
        metadata = data.get('metadata', {})
        sources.append(metadata.get('NAME', 'Unknown'))
        
        payload = data.get('payload', [])
        for rule in payload:
            rule_type, value = rule.split(',', 1)
            merged_rules.add(rule.strip())
            if rule_type in stats:
                stats[rule_type] += 1
            else:
                stats[rule_type] = 1
            stats['TOTAL'] += 1

# 构建注释部分
header_comments = [
    f"# NAME: AI规则集",
    f"# AUTHOR: SuperNG6",
    f"# REPO: https://github.com/SuperNG6/clash-ruleset",
    f"# UPDATED: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
]

# 添加统计信息
for key, value in stats.items():
    if key != 'TOTAL':
        header_comments.append(f"# {key}: {value}")
header_comments.append(f"# TOTAL: {stats['TOTAL']}")

# 添加来源信息
combined_sources = ", ".join(sources)
header_comments.append(f"# COMBINED FROM: {combined_sources}")

# 写入最终的 ai-rules.yaml
with open('ai-rules.yaml', 'w', encoding='utf-8') as f:
    for comment in header_comments:
        f.write(comment + '\n')
    f.write('payload:\n')
    for rule in sorted(merged_rules):
        f.write(f"  - {rule}\n")