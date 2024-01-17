import asyncio

import pymodbus.client as ModbusClient
from pymodbus import (
    ExceptionResponse,
    Framer,
    ModbusException,
    pymodbus_apply_logging_config,
)

import time


async def read_registers(client, offset_address, number_of_registers):
    for i in range(offset_address, number_of_registers):
        try:
        # See all calls in client_calls.py
            rr = await client.read_holding_registers(i, 1, unit= 1)
        except ModbusException as exc:  # pragma no cover
            print(f"Received ModbusException({exc}) from library")
            client.close()
            return
        if rr.isError():  # pragma no cover
            print(f"Received Modbus library error({rr})")
            client.close()
            return
        if isinstance(rr, ExceptionResponse):  # pragma no cover
            print(f"Received Modbus library exception ({rr})")
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message



async def run_async_simple_client(comm, host, port, framer=Framer.SOCKET):
    """Run async client."""
    # activate debugging
    # pymodbus_apply_logging_config("DEBUG")

    print("get client")
    if comm == "tcp":
        client = ModbusClient.AsyncModbusTcpClient(
            host,
            port=port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # close_comm_on_error=False,
            # strict=True,
            # source_address=("localhost", 0),
        )
    elif comm == "serial":
        client = ModbusClient.AsyncModbusSerialClient(
            port,
            framer=framer,
            # timeout=10,
            # retries=3,
            # retry_on_empty=False,
            # close_comm_on_error=False,
            # strict=True,
            baudrate=9600,
            bytesize=8,
            parity="N",
            stopbits=1,
            # handle_local_echo=False,
        )
   


    print("connect to server")
    await client.connect()
    # test client is connected
    assert client.connected

    print("get and verify data")
    await read_registers(client, 0, 10)
    
       


    print("close connection")
    client.close()


if __name__ == "__main__":
    start =  time.time()
    asyncio.run(
        run_async_simple_client("tcp", "127.0.0.1", 502), debug=True
    )  # pragma: no cover
    end = time.time()

    print("Time taken ", end - start)

