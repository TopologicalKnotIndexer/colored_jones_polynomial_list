from sage.all import *

import os
import mptrolley
import functools
dirnow = os.path.dirname(os.path.abspath(__file__))

# 获得扭结名称和 pd_code 的对应关系
@functools.cache
def get_com_pd_code_list() -> list:
    file = os.path.join(dirnow, "com_pd_code_list.txt")
    arr = []
    for line in open(file):
        line = line.strip()[1:-1]
        knotname, pd_code = line.split("|")
        pd_code = eval(pd_code)
        arr.append((knotname, pd_code))
    return arr

# 获得扭结名称和 pd_code 的对应关系
@functools.cache
def get_com_pd_code_dict() -> dict:
    file = os.path.join(dirnow, "com_pd_code_list.txt")
    dic = {}
    for line in open(file):
        line = line.strip()[1:-1]
        knotname, pd_code = line.split("|")
        dic[knotname] = eval(pd_code)
    return dic

@functools.cache
def get_colored_jones_for_pd_code(pd_code: str, n: int):
    pd_code = eval(pd_code)
    if pd_code == []:
        return 1
    return Knot(pd_code).colored_jones_polynomial(n)

# 试图使用乘法计算出不太好直接使用 pd_code 计算的成分
@functools.cache
def get_colored_jones_for_knotname(knot: str, n_val: int):
    if knot.find(",") == -1:
        pd_code = get_com_pd_code_dict()[knot]
        return get_colored_jones_for_pd_code(str(pd_code), n_val)
    else:
        arr = []
        for sub_knot in knot.split(","):
            sub_pd_code = get_com_pd_code_dict()[sub_knot]
            arr.append(get_colored_jones_for_pd_code(str(sub_pd_code), n_val))
        for i in range(1, len(arr)):
            arr[0] *= arr[i]
        return arr[0]

def get_colored_jones_for_index(n_val: int, k_idx: int): # 创建文件并写入，解决一个具体问题
    filename = "n%d_k%04d.txt" % (n_val, k_idx)
    filepath = os.path.join(dirnow, "sub_data", filename)
    if os.path.isfile(filepath): # 如果文件为空就删除它
        if open(filepath).read().strip() == 0:
            os.remove(filepath)
    if not os.path.isfile(filepath): # 如果文件已经存在就跳过
        knot, pd_code = get_com_pd_code_list()[k_idx]
        # line_content  = "[%s|%s]\n" % (str(get_colored_jones_for_pd_code(pd_code, n_val)), knot)
        line_content  = "[%s|%s]\n" % (str(get_colored_jones_for_knotname(knot, n_val)), knot)
        open(filepath, "w").write(line_content)

if __name__ == "__main__":
    import sys
    assert len(sys.argv) == 3
    filename, n_val, k_val = sys.argv
    n_val = int(n_val)
    k_val = int(k_val)
    get_colored_jones_for_index(n_val, k_val)