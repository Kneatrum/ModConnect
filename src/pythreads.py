import time
import queue
import threading
from interface import Device


device1 = Device(1)
device1.connect()
# device3 = Device(3)
# device3.connect()

device1_data_queue = queue.Queue()
# device3_data_queue = queue.Queue()

def method_1():
    # start_time = time.time()
    # count1 = 0
    while True:
        if device1.rtu_client_connected:
            # print(device1.read_registers())
            device1.read_registers()
        elif device1.tcp_client_connected:
            print(device1.read_registers())
            device1_data_queue.put(device1.read_registers())
        else:
            print("Ouch! No device not connected")
        time.sleep(5)
        # print("Method 1")
        # count1 += 5
    # end_time = time.time()
    # print(f"Method 1 took {end_time - start_time} seconds")

# def method_2():
#     # start_time = time.time()
#     # count2 = 0
#     while True :
#         if device3.rtu_client_connected:
#             device3.read_registers()
#             # print(device3.read_registers())
#         elif device3.tcp_client_connected:
#             device3_data_queue.put(device3.read_registers())
#             print(device3.read_registers())
#         else:
#             print("Ouch! No device not connected")
#         time.sleep(5)
#         # print("Method 2")
#         # count2 += 5
#     # end_time = time.time()
#     # print(f"Method 2 took {end_time - start_time} seconds")

def start_threads():
    start_total_time = time.time()
    dev1thread = threading.Thread(target=method_1)
    # dev2thread = threading.Thread(target=method_2)
    dev1thread.start()
    # dev2thread.start()
    dev1thread.join()
    # dev2thread.join()
    end_total_time = time.time()
    total_time1 = end_total_time - start_total_time
    print(f"\nThread time:   {total_time1} seconds")



    # start_total_time = time.time()
    # method_1()
    # method_2()
    # end_total_time = time.time()
    # total_time2 = end_total_time - start_total_time
    # print(f"Sequence time: {total_time2} seconds")
    # print(f"Ration:        {total_time2/total_time1}\n")
