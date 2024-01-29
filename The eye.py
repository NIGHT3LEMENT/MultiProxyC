import socket
import struct
import multiprocessing


def check_socks4_proxy(proxy, working_proxies):
    proxy_host, proxy_port = proxy.split(',')
    proxy_address = (proxy_host, int(proxy_port))

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(proxy_address)


        request = struct.pack('!BBH4sB', 4, 1, proxy_address[1], socket.inet_aton('0.0.0.1'), 0)


        s.send(request)


        response = s.recv(8)

        if len(response) == 8:
            version, status, port, ip = struct.unpack('!BBH4s', response)

            if status == 0x5A:
                print(f"[+] SOCKS4 Proxy ({proxy}) çalışıyor.")
                working_proxies.append(proxy)
            else:
                print(f"[-] SOCKS4 Proxy ({proxy}) çalışmıyor. Status code: {status}")
        else:
            print(f"[-] SOCKS4 Proxy ({proxy}) cevap boyutu beklenenden farklı.")

        s.close()
    except Exception as e:
        print(f"[-] SOCKS4 Proxy ({proxy}) çalışmıyor. Hata: {str(e)}")


def check_socks5_proxy(proxy, working_proxies):
    proxy_host, proxy_port = proxy.split(',')
    proxy_address = (proxy_host, int(proxy_port))

    try:
        # SOCKS5 için bağlantı
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(proxy_address)

        # SOCKS5 el sıkışma
        s.send(b'\x05\x01\x00')

        # SOCKS5 cevabını kontrol et
        response = s.recv(2)
        version, status = struct.unpack('!BB', response)

        if status == 0x00:
            print(f"[+] SOCKS5 Proxy ({proxy}) çalışıyor.")
            working_proxies.append(proxy)
        else:
            print(f"[-] SOCKS5 Proxy ({proxy}) çalışmıyor. Status: {status}")

        s.close()
    except Exception as e:
        print(f"[-] SOCKS5 Proxy ({proxy}) çalışmıyor. Hata: {str(e)}")


def process_file_chunk(start, end, lines, working_proxies):
    for i in range(start, end):
        line = lines[i]
        proxy_type, proxy = line.strip().split(',', 1)

        if proxy_type == "socks4":
            check_socks4_proxy(proxy, working_proxies)
        elif proxy_type == "socks5":
            check_socks5_proxy(proxy, working_proxies)
        else:
            print(f"[-] Geçersiz proxy türü: {proxy_type}")


if __name__ == "__main__":
    file_path = "Free_Proxy_List1.txt"  # Proxy'leri içeren dosyanın yolu
    manager = multiprocessing.Manager()
    working_proxies = manager.list()

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Mevcut işlemci sayısına göre iş parçacıklarını böl
    num_processes = multiprocessing.cpu_count()
    chunk_size = len(lines) // num_processes

    # Her bir işlemci için bir iş parçacığı oluştur
    processes = []
    for i in range(num_processes):
        start = i * chunk_size
        end = start + chunk_size if i < num_processes - 1 else len(lines)
        process = multiprocessing.Process(target=process_file_chunk, args=(start, end, lines, working_proxies))
        processes.append(process)

    # İş parçacıklarını başlat
    for process in processes:
        process.start()

    # İş parçacıklarının tamamlanmasını bekle
    for process in processes:
        process.join()

    print("\nCalisan Proxy'ler:")
    for proxy in working_proxies:
        print(proxy)
