import json
import os
import re

def reorder_json_and_files(json_filename="cave.json"):
    if not os.path.exists(json_filename):
        print(f"❌ 找不到文件: {json_filename}")
        return

    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. 确保数据按 ID 排序
    data.sort(key=lambda x: x['id'])

    new_id_counter = 1
    rename_count = 0

    # 文件名匹配正则: (旧ID)-(INDEX)_(CHANNELID)-(USERID)_(TIMESTAMP).(EXT)
    file_pattern = re.compile(r'^(\d+)(-\d+_\d+-\d+_\d+\..+)$')

    for item in data:
        old_id = item['id']
        new_id = new_id_counter

        # 2. 如果 ID 需要变更
        if old_id != new_id:
            # 处理 elements 中的文件引用
            for element in item.get('elements', []):
                if 'file' in element:
                    old_filename = element['file']
                    match = file_pattern.match(old_filename)
                    if match:
                        # 构造新文件名
                        suffix = match.group(2)
                        new_filename = f"{new_id}{suffix}"

                        # 执行磁盘物理重命名
                        if os.path.exists(old_filename):
                            try:
                                os.rename(old_filename, new_filename)
                                print(f"🚚 文件重命名: {old_filename} -> {new_filename}")
                            except Exception as e:
                                print(f"⚠️ 重命名失败 {old_filename}: {e}")

                        # 更新 JSON 中的引用
                        element['file'] = new_filename

            # 更新项本身的 ID
            item['id'] = new_id
            rename_count += 1

        new_id_counter += 1

    # 3. 保存修改后的 JSON
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"\n✨ 完成！")
    print(f"✅ 处理了 {len(data)} 个条目")
    print(f"📝 修正了 {rename_count} 个编号不连续的条目")

if __name__ == "__main__":
    reorder_json_and_files()
