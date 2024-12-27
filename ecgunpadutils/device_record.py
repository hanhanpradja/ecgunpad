import serial
import serial.tools.list_ports
import time

def record_bluetooth_data(port, timerecord=10):
    """
    Fungsi untuk merekam data dari perangkat yang terhubung melalui Bluetooth.

    Parameters:
        port (str): Nama port Bluetooth (misalnya, 'COM12' di Windows atau '/dev/ttyS0' di Linux).
        timerecord (int): Durasi waktu perekaman dalam detik (default: 10 detik).
        output_file (str): Nama file output untuk menyimpan data dalam format JSON.

    Returns:
        dict (jika sukses): JSON-like data setiap channel.
        str (jika gagal): Informasi bahwa device tidak terhubung
    """

    
    serialPort = serial.Serial(port=port, baudrate=115200, timeout=1)
 
    Raw_data = {"I": [], "II": [], "V1": []}
    t_end = time.time() + timerecord

   
    while time.time() < t_end:
        try:
            # Membaca data dari perangkat
            receivedData = serialPort.readline().decode("utf-8").strip()
            values = receivedData.split(",")
            
            if len(values) >= 3:
                # Parsing nilai dan menambahkannya ke struktur data
                value1 = float(values[0])
                value2 = float(values[1])
                value5 = float(values[2])
                
                Raw_data["I"].append(value1)
                Raw_data["II"].append(value2)
                Raw_data["V1"].append(value5)

        except ValueError:
            # Abaikan jika parsing float gagal
            continue

    return Raw_data


def get_bluetooth_ports():
    """
    Fungsi untuk mendeteksi dan mengembalikan daftar port Bluetooth yang tersedia.

    Returns:
        list: Daftar nama port Bluetooth yang tersedia di komputer.
    """
    bluetooth_ports = []
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        if "Bluetooth" in port.description or "BT" in port.description:
            bluetooth_ports.append(port.device)
    
    return bluetooth_ports

if __name__ == '__main__':
    result = get_bluetooth_ports()
    print(result)

    nama = []
    result2 = serial.tools.list_ports.comports()
    for port in result2:
        nama.append(port.description)
    
    print(nama)