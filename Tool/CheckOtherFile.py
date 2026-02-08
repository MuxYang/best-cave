import json
import os

def find_files_recursively(data_structure, files_set):
    """
    递归地遍历嵌套的列表和字典，以查找所有 "file" 键的值。
    """
    if isinstance(data_structure, dict):
        if 'file' in data_structure and isinstance(data_structure['file'], str):
            files_set.add(data_structure['file'])
        for value in data_structure.values():
            find_files_recursively(value, files_set)
    elif isinstance(data_structure, list):
        for item in data_structure:
            find_files_recursively(item, files_set)

def clean_json_data(data, missing_files):
    """
    递归地从 JSON 结构中移除包含缺失文件引用的字典项或列表项。
    """
    if isinstance(data, dict):
        # 遍历字典的键值对
        for key in list(data.keys()):
            val = data[key]
            # 如果当前值是一个包含 'file' 键的字典，且该文件在缺失列表中
            if isinstance(val, dict) and val.get('file') in missing_files:
                print(f"  - 从 JSON 中移除键 '{key}' 及其引用的缺失文件: {val['file']}")
                del data[key]
            else:
                clean_json_data(val, missing_files)
    elif isinstance(data, list):
        # 遍历列表，移除引用了缺失文件的项
        i = 0
        while i < len(data):
            item = data[i]
            if isinstance(item, dict) and item.get('file') in missing_files:
                print(f"  - 从 JSON 列表中移除引用的缺失文件: {item['file']}")
                data.pop(i)
            else:
                clean_json_data(item, missing_files)
                i += 1

def verify_files_from_json(json_filename="cave.json"):
    """
    检查JSON文件中引用的所有文件与目录实际文件是否匹配，并提供清理选项。
    """
    try:
        script_filename = os.path.basename(__file__)
    except NameError:
        script_filename = "check_files_v2.py"

    # --- 步骤 1: 递归从JSON文件中提取所有引用的文件名 ---
    expected_files = set()
    raw_data = None # 保存原始数据以便后续修改
    try:
        with open(json_filename, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            find_files_recursively(raw_data, expected_files)
    except FileNotFoundError:
        print(f"错误: 在当前目录下未找到 '{json_filename}' 文件。")
        return
    except json.JSONDecodeError:
        print(f"错误: 无法解析 '{json_filename}' 的JSON格式。")
        return
    except Exception as e:
        print(f"读取JSON文件时发生未知错误: {e}")
        return

    print(f"📄 JSON文件 '{json_filename}' 中共引用了 {len(expected_files)} 个独立文件。")

    # --- 步骤 2: 获取目录中的所有实际文件名 ---
    try:
        actual_files = {f for f in os.listdir('.') if os.path.isfile(f)}
    except OSError as e:
        print(f"读取目录时发生错误: {e}")
        return

    # --- 步骤 3: 对比文件列表 ---
    missing_files = expected_files - actual_files
    ignored_files = {json_filename, script_filename}
    extra_files = actual_files - expected_files - ignored_files

    print("\n--- 文件校验结果 ---\n")

    # --- 步骤 4: 报告结果 ---
    if not missing_files and not extra_files:
        print("✅ 非常完美！所有文件都完全匹配，没有缺失或多余的文件。")
    else:
        if missing_files:
            print(f"❌ 发现 {len(missing_files)} 个缺失文件 (在JSON中定义，但文件夹中不存在)。")
        else:
            print("✅ 文件完整性良好，JSON中提到的所有文件都存在。")

        if extra_files:
            print(f"⚠️ 发现 {len(extra_files)} 个多余文件 (存在于文件夹中，但未在JSON中引用)。")
        else:
            print("✅ 目录整洁，没有发现JSON以外的多余文件。")

    # --- 步骤 5: (新增) 交互式清理逻辑 ---
    
    # 1. 处理多余的物理文件
    if extra_files:
        print("\n" + "!"*30)
        confirm_del_extra = input(f"❓ 是否要从磁盘中删除这 {len(extra_files)} 个多余文件？(y/n): ").lower()
        if confirm_del_extra == 'y':
            for f_to_del in extra_files:
                try:
                    os.remove(f_to_del)
                    print(f"  - 已删除: {f_to_del}")
                except Exception as e:
                    print(f"  - 删除失败 {f_to_del}: {e}")
            print("✨ 多余文件清理完成。")

    # 2. 处理 JSON 中失效的条目
    if missing_files:
        print("\n" + "!"*30)
        confirm_clean_json = input(f"❓ 是否从 '{json_filename}' 中移除这 {len(missing_files)} 个缺失文件的引用记录？(y/n): ").lower()
        if confirm_clean_json == 'y':
            print("正在清理 JSON 数据...")
            clean_json_data(raw_data, missing_files)
            
            try:
                with open(json_filename, 'w', encoding='utf-8') as f:
                    # ensure_ascii=False 保证中文字符不被转义，indent=4 保持格式美观
                    json.dump(raw_data, f, ensure_ascii=False, indent=4)
                print(f"✨ '{json_filename}' 已更新，无效记录已移除。")
            except Exception as e:
                print(f"写入 JSON 文件时出错: {e}")

    print("\n--- 报告及清理流程结束 ---")

if __name__ == "__main__":
    verify_files_from_json()