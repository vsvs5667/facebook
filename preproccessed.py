import dpkt
import socket
import os

import dpkt

def process_pcapng_file(filename):
    # 打开pcapng文件并读取数据包
    with open(filename, 'rb') as file:
        pcapng = dpkt.pcapng.Reader(file)

        # 创建一个列表用于存储处理后的数据包
        processed_packets = []

        # 遍历每个数据包
        for timestamp, packet in pcapng:

            # 解析以太网报头
            eth = dpkt.ethernet.Ethernet(packet)

            # 删除以太网报头
            if isinstance(eth.data, dpkt.ip.IP):
                ip = eth.data
                eth.data = ip.data
                packet = bytes(eth)

            # 解析IP数据报报头
            ip = eth.data

            # 删除IP数据报报头的IP地址
            if isinstance(ip.data, dpkt.tcp.TCP) or isinstance(ip.data, dpkt.udp.UDP):
                ip.src = b'\x00\x00\x00\x00'
                ip.dst = b'\x00\x00\x00\x00'
                packet = bytes(ip)

                # 删除没有负载的数据包（TCP握手时SYN、ACK设置为1以及FIN设置为1的数据包）或者DNS数据段
                if len(ip.data.data) != 0 and not (ip.data.data.startswith(b'\x00') and
                                                  (ip.data.data[13] & 0x1f) == dpkt.tcp.TH_ACK and
                                                  (ip.data.data[13] & dpkt.tcp.TH_FIN) != 0):
                    processed_packets.append(packet)

        # 对处理后的数据包进行进一步处理
        processed_packets = process_packets(processed_packets)

        return processed_packets

def process_packets(packets):
    processed_packets = []

    for packet in packets:
        # 将UDP报头填充至20字节长度
        if isinstance(packet[14], dpkt.udp.UDP):
            udp = packet[14]
            udp.data = udp.data.ljust(20, b'\x00')
            packet[14] = udp

        # 将原始数据包转为字节向量
        byte_vector = bytes(packet)

        # 截断超过1500的向量，不足1500长度的填充0
        if len(byte_vector) > 1500:
            byte_vector = byte_vector[:1500]
        else:
            byte_vector = byte_vector.ljust(1500, b'\x00')

        # 将向量的每个元素除以255来规范化字节向量
        normalized_vector = [i / 255 for i in byte_vector]

        # 添加到处理后的数据包列表中
        processed_packets.append(normalized_vector)

    return processed_packets

# 调用处理函数，传入pcapng文件路径
processed_packets = process_pcapng_file('D:\\VMshare\\success.pcapng')
print(processed_packets)

# 打印处理后的数据包
for packet in processed_packets:
    print(packet)

