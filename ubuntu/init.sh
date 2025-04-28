#!/bin/bash
# 初始化脚本

function fix_chmod() {
    find /etc/ -type d -exec chmod ug+x {} \;
}

fix_chmod
echo Inited.
# 应在最后启动 Supervisord
exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf