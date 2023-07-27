import dpkt

def process_pcapng_file(filename):
    # 打开pcapng文件并读取数据包
    with open(filename, 'rb') as file:
        pcapng = dpkt.pcapng.Reader(file)

        # 创建一个列表用于存储处理后的数据包
        processed_packets = []

        # 遍历每个数据包
        for timestamp, packet in pcapng:
            # print(packet)
            # 解析以太网报头
            eth = dpkt.ethernet.Ethernet(packet)   #将原始数据包 packet 解析为以太网帧对象 eth, eth.data include ip except eth,ip.data include tcp except ip

            # 删除以太网报头
            if isinstance(eth.data, dpkt.ip.IP):    #only ipv4   eth.data 表示以太网帧的数据部分，也就是帧的有效载荷。在大多数情况下，帧的数据部分会携带上层协议的头部，其中最常见的情况是 IP 头和 TCP 或 UDP 头。具体来说，在常见的 TCP/IP 网络通信中，数据包的嵌套关系如下：以太网帧（Ethernet Frame）以太网报头（Ethernet Header）数据部分（Payload，通常包含 IP 头和上层协议头）IP 数据包（IP Packet）IP 头（IP Header）上层协议数据（通常是 TCP 头或 UDP 头）TCP 数据包（TCP Packet）或 UDP 数据包（UDP Packet）TCP 头（TCP Header）或 UDP 头（UDP Header）应用层数据（Application Layer Data）
                ip = eth.data
                # 删除IP数据报报头的IP地址
                ip.src = b'\x00\x00\x00\x00'
                ip.dst = b'\x00\x00\x00\x00'
            # 解析IP数据报报头
            else:
                continue
            if isinstance(ip.data, dpkt.tcp.TCP):   # ip.data include tcp except ip, ip.data.data may explain payload or application layer data
                tcp = ip.data
                tcp.sport = 0
                tcp.dport = 0
                # tcp_data = tcp.data
                # tcp.data = b''
                # tcp_header_padded = bytes(tcp).ljust(40, b'\x00')
                # ip.data = tcp_header_padded + tcp_data
            # padding udp packet to 20 bytes
            elif isinstance(ip.data, dpkt.udp.UDP):
                udp = ip.data
                udp.sport = 0
                udp.dport = 0
                udp_data = udp.data
                udp.data = b''
                udp_header_padded = bytes(udp).ljust(20, b'\x00')
                ip.data = udp_header_padded + udp_data
            else:
                continue
            #  erase FIN=1
            # tcp_header = bytes(tcp)
            # print(tcp_header[13] & dpkt.tcp.TH_FIN)
            # erase SYN=1 AND ACK=1
            # print(bool(tcp_header[13] & dpkt.tcp.TH_SYN) and bool(tcp_header[13] & dpkt.tcp.TH_ACK))
            # erase SYN=1 OR ACK=1 ?
            # padding udp header to 20 bytes
            # erase no payload
            if len(tcp.data) != 0 :
                processed_packets.append(bytes(ip))   # if no bytes, it will display string: dpkt.ip.IP's __repr__() result, so if you want to display b'',you should use bytes(ip)
        # print(processed_packets)
        # 对处理后的数据包进行进一步处理
        processed_packets = process_packets(processed_packets)

        return processed_packets

def process_packets(packets):
    processed_packets = []

    for packet in packets:
        # 截断超过1500的向量，不足1500长度的填充0
        if len(packet) > 1500:
            byte_vector = packet[:1500]
        else:
            byte_vector = packet.ljust(1500, b'\x00')
        print(byte_vector)

        # 将向量的每个元素除以255来规范化字节向量
        normalized_vector = [i / 255 for i in byte_vector]

        # 添加到处理后的数据包列表中
        processed_packets.append(normalized_vector)

    return processed_packets

# 调用处理函数，传入pcapng文件路径
processed_packets = process_pcapng_file('/home/who/Downloads/facebook-main/success.pcapng')


#打印处理后的数据包
for packet in processed_packets:
    print(packet)

