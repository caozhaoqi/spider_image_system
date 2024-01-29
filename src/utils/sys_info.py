# # import psutil
# import subprocess
# import platform
#
# from loguru import logger
#
#
# def get_exe_process_info(exe_path):
#     # 获取进程ID (PID)
#     pid = None
#     try:
#         result = subprocess.run(['tasklist', '/FI', 'imagename eq {exe_path}'.format(exe_path=exe_path)],
#                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         lines = result.stdout.splitlines()
#         for line in lines:
#             if exe_path in line:
#                 if exe_path:
#                     pid = exe_path  # 获取PID，假设只有一个进程匹配
#                 break
#     except Exception as e:
#         logger.warning(str(e))
#         return None
#
#     if pid is None:
#         logger.info(pid)
#         return None  # 没有找到匹配的进程
#
#     try:
#         # 获取CPU和内存使用情况
#         process = psutil.Process(pid)
#         cpu_percent = process.cpu_percent(interval=1)  # 1秒内CPU使用率百分比
#         memory_info = process.memory_info()  # 获取内存使用情况
#         memory_percent = process.memory_percent()  # 进程占用的物理内存百分比
#         return {
#             'pid': pid,
#             'cpu_percent': str(cpu_percent),
#             'memory_info': str(memory_info._asdict()),  # 使用 _asdict() 获取字典格式的信息
#             'memory_percent': str(memory_percent),
#         }
#     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as ee:
#         logger.warning(str(ee))
#         return None  # 进程不存在或没有足够的权限访问进程信息
#     except Exception as e:
#         logger.warning(str(e))
#         return None  # 其他错误情况
#     # finally:
#         # if pid is not None:  # 确保关闭进程的连接，避免资源泄漏或其他问题
#         #     psutil.Process(int(pid)).kill()
#
#
# def get_gpu_info():
#     if platform.system() == "Windows":
#         return "Windows GPU info not implemented yet"  # Windows下的GPU信息获取需要其他工具或库，例如NVML或第三方库。此处仅为占位符。
#     else:  # Linux/macOS等其他系统下可以使用类似nvidia-smi的方法，但具体实现会有所不同。此处仅为占位符。
#         return "Linux/macOS GPU info not implemented yet"
#         # 可以考虑使用类似于nvidia-smi的命令或库来获取GPU信息。具体实现会因操作系统和硬件而异。
#
#
# if __name__ == '__main__':
#     ret = get_exe_process_info(r'sis_v1.0.2_beta.exe')
#     logger.info(ret)
