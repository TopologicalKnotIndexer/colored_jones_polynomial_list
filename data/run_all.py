from ProcessWrapQueue import ProcessWrapQueue
from ProcessWrap import ProcessWrap

import os
import time
import shlex

TIME_LIMIT_SEC = 60 # 超时时长
dirnow = os.path.dirname(os.path.abspath(__file__))

def main(process_cnt: int): # 多个任务队列
    pw_queue_list = []
    for _ in range(process_cnt): # 创建任务队列组
        pw_queue = ProcessWrapQueue()
        pw_queue_list.append(pw_queue)

    for pw_queue in pw_queue_list: # 启动所有队列
        pw_queue.set_queue_status("RUN")

    for idx in range(1783 * 2): # 分配所有任务
        n_val     = 2 + (idx % 2)
        k_val     = idx // 2
        queue_idx = idx % process_cnt # 队列编号
        pw        = ProcessWrap(shlex.split("bash -c 'python3 get_colored_jones_2_and_3.py %d %d'" % (n_val, k_val)), os.getcwd())
        pw_queue_list[queue_idx].add_process_wrap(pw)

    def kill_run_too_long():    # 杀死所有运行时间太长的任务
        for pw_queue in pw_queue_list:
            with pw_queue.lock: # 加锁
                for pw in pw_queue.run_queue:
                    if pw.get_status_time_now() >= TIME_LIMIT_SEC and pw.get_status()["status"] == "RUN":
                        pw.kill_task()

    while True:
        os.system("clear")
        for idx, pw_queue in enumerate(pw_queue_list): # 显示日志信息
            print("ProcessWrapQueue_%02d: " % idx, pw_queue.get_queue_status_brief())
            pw_queue.dump_queue_status_to_file(os.path.join(dirnow, "log", "ProcessWrapQueue_%02d.log" % idx))
        kill_run_too_long() # 杀死运行时间太长的进程
        time.sleep(10)

if __name__ == "__main__":
    main(10)