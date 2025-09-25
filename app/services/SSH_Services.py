import re
import asyncio
import asyncssh
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState


ssh_sessions = {}
async def read_from_ssh(process, websocket):
    try:
        while True:
            data = await process.stdout.read(1024)
            if data:
                try:
                    await websocket.send_text(data)
                except WebSocketDisconnect:
                    break
            else:
                try:
                    await websocket.send_text("** SSH session ended **")
                    await websocket.send_text("__RECONNECT__")
                except WebSocketDisconnect:
                    break
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass


async def read_from_ws(process, websocket):
    try:
        while True:
            try:
                command = await websocket.receive_text()
            except WebSocketDisconnect:
                 break

            process.stdin.write(command + '\n')

    except asyncio.CancelledError:
        pass


async def handle_ssh_session(websocket: WebSocket, username: str):
    await websocket.accept()
    conn = ssh_sessions.get(username)

    if not conn:
        await websocket.send_json({"error": "No active SSH session"})
        await websocket.close()
        return

    try:
        process = await conn.create_process(term_type="xterm")

        read_ssh = asyncio.create_task(read_from_ssh(process, websocket))
        read_ws = asyncio.create_task(read_from_ws(process, websocket))

        done, pending = await asyncio.wait(
            [read_ssh, read_ws],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

    except Exception as e:
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_json({"error": str(e)})


async def run_command(conn, command: str):
    try:
        result = await conn.run(command)
        if result.stdout.strip():
            return result.stdout.strip()
        else:
            result = result.stderr.strip()
            if not result: # if empty then command succeeded 
                return "Command Executed Successfully"
            else:
                return result
    except Exception as e:
        raise RuntimeError(f"SSH command failed: {str(e)}")

# async def test():
#     try:
#         async with asyncssh.connect(
#             SSH_SWITCH_IP,
#             username=SSH_USERNAME,
#             password=SSH_PASSWORD
#         ) as conn: 
#             result = await run_command(conn, "config vlan add 2")
#             print("result is", result)
#     except Exception as e:
#         raise RuntimeError(f"SSH command failed: {str(e)}") 

# if __name__ == "__main__":
#     asyncio.run(test())

def parse_top_output(output: str):

    lines = output.splitlines()

    for line in lines:
        if line.startswith("%Cpu(s):"):
            match = re.findall(r"([\d\.]+)\s+id", line)
            if match:
                # print("in top", float(match[0]))
                return 100 - float(match[0])
                
    raise ValueError("CPU idle value not found in output")

def parse_free_output(output: str):

    lines = output.splitlines()

    for line in lines:
        if line.startswith("Mem:"):
            parts = line.split()
            total = float(parts[1][:-2])
            available = float(parts[6][:-2])
            # print(total)
            # print(available)
            mem_percentage = ((total - available)/ total) * 100
            return mem_percentage
        
    raise ValueError("Mem value not found in output")


def parse_fan_output(cli_output: str):
    fans = []
    lines = cli_output.strip().splitlines()
    
    # Find the section after "show platform fan"
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Drawer"):
            start_idx = i + 1
            break
    
    if start_idx is None:
        return fans  # no data found
    
    # Parse the fan lines
    for line in lines[start_idx:]:
        parts = re.split(r"\s{2,}", line.strip())  # split by 2+ spaces
        if len(parts) < 7:
            continue
        fan = {
            # "drawer": parts[0],
            # "led": parts[1],
            "fan": parts[2],
            # "speed": parts[3],
            # "direction": parts[4],
            "presence": parts[5],
            "status": parts[6],
            # "timestamp": parts[7] if len(parts) > 7 else None,
        }
        fans.append(fan)
    
    return fans


def parse_psu_output(cli_output: str):
    psus = []
    lines = cli_output.strip().splitlines()

    # Find the section after "PSU"
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("PSU"):
            start_idx = i + 1
            break

    if start_idx is None:
        return psus  # no data found

    # Parse PSU lines
    for line in lines[start_idx:]:
        parts = re.split(r"\s{2,}", line.strip())  # split by 2+ spaces
        if len(parts) < 8:
            continue

        psu = {
            "psu": parts[0],        # PSU1 / PSU2
            # "model": parts[1],      # YM-1401A
            # "serial": parts[2],     # serial number
            # "hw_rev": parts[3],     # N/A
            "voltage_v": parts[4],  # Voltage (V)
            # "current_a": parts[5],  # Current (A)
            # "power_w": parts[6],    # Power (W)
            "status": parts[7],     # OK / NOT OK
            # "led": parts[8] if len(parts) > 8 else None,  # green / red
        }
        psus.append(psu)

    return psus

def parse_temperature_output(cli_output: str):
    temperatures = []
    lines = cli_output.strip().splitlines()

    # Find the section after the header, assuming the header line starts with "Sensor".
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Sensor"):
            start_idx = i + 1
            break
    
    if start_idx is None:
        return temperatures  # No data found

    # Parse the temperature sensor lines
    for line in lines[start_idx:]:
        parts = re.split(r"\s{2,}", line.strip())  # Split by 2 or more spaces
        
        # Ensure the line has enough parts to be a valid sensor entry.
        # We expect at least Sensor, Temperature (C), and Status.
        if len(parts) < 5:
            continue
            
        sensor = {
            "sensor": parts[0],
            "temperature_celsius": parts[2],
            "status": parts[4],
        }
        temperatures.append(sensor)
    
    return temperatures

async def switch_status(websocket: WebSocket, username: str):

    await websocket.accept()
    conn = ssh_sessions.get(username)

    if not conn:
        await websocket.send_json({"error": "No active SSH session"})
        await websocket.close()
        return
    try:
            while True:
                cpu_result = await run_command(conn, "top -b -n 1")
                cpu_usage_percentage = parse_top_output(cpu_result)
                # print("inside switch status cpu = ", cpu_usage_percentage)

                memory_result = await run_command(conn, "free -h")
                mem_percentage = parse_free_output(memory_result)
                # print("inside switch status mem perc = ", mem_percentage)

                #  Fans
                # fan_result = await run_command(conn, "show platform fan")
                # fans = parse_fan_output(fan_result)

                # # PSUs
                # psu_result = await run_command(conn, "show platform psustatus")
                # psus = parse_psu_output(psu_result)

                # # Temperature
                # temp_result = await run_command(conn, "show platform temperature")
                # temp = parse_psu_output(temp_result)

                fans = {
                    "FAN-1F":"40%",
                    "FAN-1R": "40%",
                    "FAN-2F": "40%",
                    "FAN-2R": "40%",
                    "FAN-3F": "40%",
                    "FAN-3R": "40%",
                    "FAN-4F": "40%",
                    "FAN-4R": "40%",
                    "FAN-5F": "40%",
                    "FAN-5R": "40%",
                    "PSU-1 FAN-1": "14%",
                    "PSU-2 FAN-1": "0%"
                }

                psus = {
                    "PSU 1":{"Power": "79.00", "Status": "OK", "LED": "green"},
                    "PSU 2":{"Power": "0.00", "Status": "NOT OK", "LED": "red"}
                }

                temp = {
                    "PSU-1 temp sensor 1":"31",
                    "PSU-2 temp sensor 2":"23",
                    "Temp sensor 1":"31.5",
                    "Temp sensor 2":"23.5",
                    "Temp sensor 3":"24.5",
                    "Temp sensor 4":"24"
                }
                await websocket.send_json({
                    "cpu_used_percent": cpu_usage_percentage,
                    "memory_used_percent": mem_percentage,
                    "fans": fans,
                    "psus": psus,
                    "temp":temp

                })

                await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("Client disconnected, stopping...")

    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")