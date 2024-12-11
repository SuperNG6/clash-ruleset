import yaml
import os
from datetime import datetime

# 定义规则文件路径
rule_files = ['rules/Gemini.yaml', 'rules/OpenAI.yaml', 'rules/Claude.yaml', 'rules/CustomRules.yaml']

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

def extract_metadata(file_path):
    metadata = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#'):
                parts = line[1:].strip().split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    metadata[key.strip().upper()] = value.strip()
            else:
                break  # 假设元数据注释放在文件顶部的注释中
    return metadata

for file in rule_files:
    if not os.path.exists(file):
        print(f"文件 {file} 不存在，跳过。")
        continue

    metadata = extract_metadata(file)
    source_name = metadata.get('NAME', 'Unknown')
    sources.append(source_name)

    # 解析 YAML 文件
    with open(file, 'r', encoding='utf-8') as f:
        # 跳过顶部的注释行
        lines = []
        for line in f:
            if line.startswith('#'):
                continue
            lines.append(line)
        try:
            data = yaml.safe_load(''.join(lines))
        except yaml.YAMLError as e:
            print(f"解析 YAML 文件 {file} 时出错: {e}")
            continue

    payload = data.get('payload', [])
    for rule in payload:
        if isinstance(rule, str):
            rule = rule.strip()
            if not rule:
                continue
            parts = rule.split(',', 1)
            if len(parts) != 2:
                continue
            rule_type, value = parts
            rule_type = rule_type.strip().upper()
            value = value.strip()
            if rule_type and value:
                merged_rules.add(f"{rule_type},{value}")
                if rule_type in stats:
                    stats[rule_type] += 1
                else:
                    stats[rule_type] = 1
                stats['TOTAL'] += 1

# 构建注释部分
header_comments = [
    f"# NAME: AI规则集",
    f"# AUTHOR: SuperNG6",
    f"# REPO: https://github.com/SuperNG6/clash-ruleset", # 请确保此链接正确
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

print("合并完成，生成 ai-rules.yaml。")