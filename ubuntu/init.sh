#!/bin/bash
# 初始化脚本


echo Inited.
# 应在最后启动 Supervisord
exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf