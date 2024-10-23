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

def get_colored_jones(pd_code: list, n: int):
    if pd_code == []:
        return 1
    print(pd_code)
    return Knot(pd_code).colored_jones_polynomial(n)

def get_colored_jones_for_index(n_val: int, k_idx: int): # 创建文件并写入，解决一个具体问题
    filename = "n%d_k%04d.txt" % (n_val, k_idx)
    filepath = os.path.join(dirnow, "sub_data", filename)
    if os.path.isfile(filepath): # 如果文件为空就删除它
        if open(filepath).read().strip() == 0:
            os.remove(filepath)
    if not os.path.isfile(filepath): # 如果文件已经存在就跳过
        knot, pd_code = get_com_pd_code_list()[k_idx]
        line_content  = "[%s|%s]\n" % (str(get_colored_jones(pd_code, n_val)), knot)
        open(filepath, "w").write(line_content)

def question_function(question_index, common_context): # 用于计算染色琼斯
    knot_index = question_index // 2
    n_index    = question_index %  2
    n_val      = n_index + 2
    get_colored_jones_for_index(n_val, knot_index)

if __name__ == "__main__":
    question_count = len(get_com_pd_code_list()) * 2
    process_count  = 36
    mptrolley.solve_problem_with_multiprocessing(question_function, {}, question_count, process_count)