import json
from colorama import Fore, Style

def highlight_diff(str1, str2):
    r"""
        比较两个字符串的差异，并且将不同的字符显示成红色
        
        Args:
            params (`str1`):
                字符串1
            params (`str2`):
                字符串2
    """
    
    result = ''
    for char1, char2 in zip(str1, str2):
        if char1 != char2:
            result += Fore.RED + char1 + Style.RESET_ALL
        else:
            result += char1
    # 处理长度不一致的情况
    if len(str1) > len(str2):
        result += Fore.RED + str1[len(str2):] + Style.RESET_ALL
    elif len(str2) > len(str1):
        result += Fore.RED + str2[len(str1):] + Style.RESET_ALL
    return result


def read_jsonl(file_path) -> list:
    r"""
        将jsonl的文件转化成为列表
        
        Args:
            params (`file_path`):
                文件路径
    """
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data


if __name__ == "__main__":
    str1 = "example string"
    str2 = "esample string"
    print(highlight_diff(str1, str2))
