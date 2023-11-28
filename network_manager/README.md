
`sudo ip link set dev wlan0 up`  打开WIFI
`nmcli dev wifi rescan` 重新扫描WIFI，不返回任何结果
`nmcli dev wifi list`  列出扫描到到Wi-Fi
`nmcli dev status`   获取网络设备状态
`nmcli dev wifi connect {ssid} `  连接到Wi-Fi
`nmcli dev wifi connect {ssid} password {password}`  连接到Wi-Fi，包括秘密
`nmcli dev  disconnect {device}`  断开指定设备连接

`sudo ip link set dev {device} up/down`        打开/关闭指定网络设备
`sudo ip link set dev {device} address {mac}`  更改指定设备到MAC地址