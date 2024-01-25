"""
This module contains methods used in polling registers 
from devices we are connected to.
"""
# from pymodbus.client import ModbusTcpClient, ModbusSerialClient
# from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.constants import Endian
# from file_handler import FileHandler
import concurrent.futures
import time
import multiprocessing


# class RegisterReader:
#     def __init__(self):
#         self.table_views =[]
#         self.file_handler = FileHandler()

    
#     def add_table_view(self, table_view):
#         if table_view not in self.table_views:
#             self.table_views.append(table_view)

#     def remove_table_view(self, table_view):
#         self.table_views.remove(table_view)

#     def update_table_view(self, data):
#         for index, table_view in enumerate(self.table_views):
#             table_view.update(data[index])


#     def read_registers(self) -> list:
#         time.sleep(1)
#         return []
        
    
#     def mimisijui(self):
#         with concurrent.futures.ProcessPoolExecutor() as executor:
#             registers_addresses = [[1], [2], [3], [4], [5], [6], [7]]
#             results = executor.map(self.read_registers, registers_addresses)

#             for result in results:
#                 print(result)
#         return results


# register_reader = RegisterReader()

def read_registers():
    time.sleep(1)

def read_registers_v2(v):
    time.sleep(v)

def read_registers_v3(v) -> str:
    print(f'Sleeping for {v} seconds')
    time.sleep(v)
    return f'done sleeping {v} seconds'

def method1():
    p2 = multiprocessing.Process(target=read_registers)
    p1 = multiprocessing.Process(target=read_registers)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def method2():
    processes = []
    for _ in range(10):
        p = multiprocessing.Process(target=read_registers_v2, args=[1.5])
        p.start()
        processes.append(p)

    for process in processes:
        process.join()


def method3():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        f1 = executor.submit(read_registers_v3, 1)
        f2 = executor.submit(read_registers_v3, 1)
        print(f1.result())
        print(f2.result())


def method4():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        secs = [5, 4, 3, 2, 1]
        results = [executor.submit(read_registers_v3, sec) for sec in secs]

        for f in concurrent.futures.as_completed(results):
            print(f.result())

def method5():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        secs = [5, 4, 3, 2, 1]
        results = executor.map(read_registers_v3, secs)

        for result in results:
            print(result)


    
if __name__ == '__main__':
    start = time.perf_counter()

    method5()

    finish = time.perf_counter()
    print(f'Time taken: {finish - start} seconds')