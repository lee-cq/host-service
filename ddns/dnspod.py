#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@File Name  : dnspod.py
@Author     : LeeCQ
@Date-Time  : 2020/3/20 19:50


"""

import logging
import json
from urllib import request, parse

logger = logging.getLogger("dnspod")


class DnspodCommon:
    """Some Common Method for Dnspod"""
    UA = 'DNS for Python/0.0.3(lcq@leecq.cn)'

    def __init__(self, id_, token, format_='json', lang='cn', domain_grade='DP_Plus'):
        self.api_token = ','.join([id_, token])
        self.format = format_
        self.lang = lang
        self.domain_grade = domain_grade

    def post(self, url: str, data: dict = dict, header: dict = dict) -> dict:
        """使用post方法调用接口"""
        err_code, err_message = 0, ''
        header.update({'User-Agent': self.UA})

        data.update(self.public_arguments())
        data = parse.urlencode(data).encode('utf8')

        req = request.Request(url, data, header)
        res = request.urlopen(req)
        if res.status != 200:
            err_code, err_message = -999, f'服务器非200返回！status_code={res.status}'
        elif res.readable():
            try:
                return json.loads(res.read())
            except Exception as e:
                logger.warning(f'不能以JSON字符串解析 > {e}')
                err_code = -998
                err_message = f'不能以JSON字符串解析 > {e}'

        return dict({'status': {'code': err_code, 'message': err_message}})

    def public_arguments(self) -> dict:
        """请求中的公共参数

        API-DOC: https://www.dnspod.cn/docs/info.html#common-parameters

        login_token 用于鉴权的 API Token
        format {json,xml} 返回的数据格式，可选，默认为xml，建议用json
        lang {en,cn} 返回的错误语言，可选，默认为en，建议用cn
        error_on_empty {yes,no} 没有数据时是否返回错误，可选，默认为yes，建议用no
        user_id 用户的ID，可选，仅代理接口需要， 用户接口不需要提交此参数
        """
        pub = dict()
        pub.setdefault('login_token', self.api_token)
        pub.setdefault('format', self.format)
        pub.setdefault('lang', self.lang)
        return pub

    def api_version(self):
        """获取API版本号"""
        url = 'https://dnsapi.cn/Info.Version'
        return self.post(url, dict())

    def user_info(self):
        """用户信息"""
        return self.post('https://dnsapi.cn/User.Detail', dict())

    def user_log(self):
        """获取用户日志"""
        return self.post('https://dnsapi.cn/User.Log', dict())

    def api_record_type(self, domain_grade=None):
        """获取记录类型

        D_Free、D_Plus、D_Extra、D_Expert、D_Ultra
        DP_Free、DP_Plus、DP_Extra、DP_Expert、DP_Ultra
        """
        domain_grade = domain_grade or self.domain_grade
        return self.post('https://dnsapi.cn/Record.Type', {'domain_grade': domain_grade})

    def api_record_line(self, domain):
        """https://dnsapi.cn/Record.Line"""

        return self.post('https://dnsapi.cn/Record.Line', {'domain': domain})


class DnspodDNS(DnspodCommon):
    """DNS of DNSPOD API for Python. """

    def record_list(self, domain, offset=0, length=100,
                    sub_domain=None, record_type=None, record_line='默认',
                    record_line_id=None, keyword=None
                    ):
        """列出解析记录

        公共参数
        domain_id 或 domain, 分别对应域名ID和域名, 提交其中一个即可
        offset 记录开始的偏移，第一条记录为 0，依次类推，可选（仅当指定 length 参数时才生效）
        length 共要获取的记录数量的最大值，比如最多获取20条，则为20，最大3000.可选
        sub_domain 子域名，如果指定则只返回此子域名的记录，可选
        record_type 记API记录类型获得，大写英文，比如：A，可选
        record_line 记录线路，通录类型，通过过API记录线路获得，中文，比如：默认，可选
        record_line_id 线路的ID，通过API记录线路获得，英文字符串，比如：‘10=1’，可选
                【需要获取特定线路的解析记录时，record_line 和 record_line_id 二者传其一即可，系统优先取 record_line_id】
        keyword，搜索的关键字，如果指定则只返回符合该关键字的记录，可选
                【指定 keyword 后系统忽略查询参数 sub_domain，record_type，record_line，record_line_id】
        """
        url = 'https://dnsapi.cn/Record.List'
        data = dict(domain=domain, offset=offset, length=length)
        if sub_domain:
            data.update(sub_domain=sub_domain)
        if record_line:
            data.update(record_line=record_line)
        if record_type:
            data.update(record_type=record_type)
        if record_line_id:
            data.update(record_line_id=record_line_id)
        if keyword:
            data.update(keyword=keyword)
        logger.debug(f'Record_List: {data}')
        return self.post(url, data)

    def record_add(self, rr, domain, record_type, value, record_line='默认',
                   mx=None, ttl=600, status='enable', weight=None, record_line_id=None
                   ):
        """添加解析记录

        :param domain: 分别对应域名ID和域名, 提交其中一个即可
        :param rr: 主机记录, 如 www，可选，如果不传，默认为 @
        :param record_type: 记录类型，通过API记录类型获得，大写英文，比如：A，必选
        :param record_line: 记录线路，通过API记录线路获得，中文，比如：默认，必选
        :param record_line_id: 线路的ID，通过API记录线路获得，英文字符串，比如：‘10=1’
                【record_line 和 record_line_id 二者传其一即可，系统优先取 record_line_id】
        :param value: 记录值, 如 IP:200.200.200.200, CNAME: cname.dnspod.com., MX: mail.dnspod.com.，必选
        :param mx: {1-20} MX优先级, 当记录类型是 MX 时有效，范围1-20, mx记录必选
        :param ttl: {1-604800} TTL，范围1-604800，不同等级域名最小值不同，可选
        :param status: [“enable”, “disable”]，记录状态，默认为”enable”，
                如果传入”disable”，解析不会生效，也不会验证负载均衡的限制，可选
        :param weight: 权重信息，0到100的整数，可选。仅企业 VIP 域名可用，0 表示关闭，留空或者不传该参数，表示不设置权重信息
        """
        data = dict(sub_domain=rr, domain=domain, record_line=record_line, record_type=record_type,
                    value=value, ttl=ttl, status=status,
                    )
        if record_type == 'MX':
            data.update(mx=mx or 10)
        if weight is not None:
            data.update(weight=weight)
        if record_line_id is not None:
            data.update(record_line_id=record_line_id)
        return self.post('https://dnsapi.cn/Record.Create', data)

    def record_update(self, record_id, rr, domain, record_type, value,
                      ttl=600, record_line='默认', record_line_id=None, mx=None, status='enable', weight=None):
        """修改解析记录

        :param domain: 分别对应域名ID和域名, 提交其中一个即可
        :param record_id: 记录ID，必选
        :param rr: 主机记录, 如 www，可选，如果不传，默认为 @
        :param record_type: 记录类型，通过API记录类型获得，大写英文，比如：A，必选
        :param record_line: 记录线路，通过API记录线路获得，中文，比如：默认，必选
        :param record_line_id: 线路的ID，通过API记录线路获得，英文字符串，比如：‘10=1’
                【record_line 和 record_line_id 二者传其一即可，系统优先取 record_line_id】
        :param value: 记录值, 如 IP:200.200.200.200, CNAME: cname.dnspod.com., MX: mail.dnspod.com.，必选
        :param mx: {1-20} MX优先级, 当记录类型是 MX 时有效，范围1-20, mx记录必选
        :param ttl: {1-604800} TTL，范围1-604800，不同等级域名最小值不同，可选
        :param status: [“enable”, “disable”]，记录状态，默认为”enable”，
                如果传入”disable”，解析不会生效，也不会验证负载均衡的限制，可选
        :param weight: 权重信息，0到100的整数，可选。仅企业 VIP 域名可用，0 表示关闭，留空或者不传该参数，表示不设置权重信息
        """
        data = dict(record_id=record_id, sub_domain=rr, domain=domain, record_line=record_line,
                    record_type=record_type, value=value, ttl=ttl, status=status,
                    )
        if record_type == 'MX':
            data.update(mx=mx or 10)
        if weight is not None:
            data.update(weight=weight)
        if record_line_id is not None:
            data.update(record_line_id=record_line_id)
        return self.post('https://dnsapi.cn/Record.Modify', data=data)

    def record_delete(self, domain, record_id):
        """删除解析记录

        :param domain:, 分别对应域名ID和域名, 提交其中一个即可
        :param record_id: 记录ID，必选
        """
        return self.post(' https://dnsapi.cn/Record.Remove', dict(domain=domain, record_id=record_id))

    def record_ddns(self, record_id, rr, domain, value, record_line='默认', record_line_id=None):
        """DDNS

        :param domain:, 分别对应域名ID和域名, 提交其中一个即可
        :param record_id: 记录ID，必选
        :param rr: 主机记录，如 www
        :param record_line: 记录线路，通过API记录线路获得，中文，比如：默认，必选
        :param record_line_id: 线路的ID，通过API记录线路获得，英文字符串，
                               比如：‘10=1’ 【record_line 和 record_line_id 二者传其一即可，系统优先取 record_line_id】
        :param value: IP地址，例如：6.6.6.6，可选
        """
        data = dict(sub_domain=rr, record_id=record_id, domain=domain, value=value, record_line=record_line)
        if not record_line_id:
            data.update(record_line_id=record_line_id)
        return self.post(' https://dnsapi.cn/Record.Ddns', data)

    def record_remark(self, domain, record_id, remark):
        """更新设置备注

        :param domain, 分别对应域名ID和域名, 提交其中一个即可
        :param record_id 记录ID，必选
        :param remark 域名备注，删除备注请提交空内容，必选
        :return:
        """

        return self.post('https://dnsapi.cn/Record.Remark', dict(domain=domain, record_id=record_id, remark=remark))

    def record_info(self, domain, record_id):
        """获取记录的信息

        :param domain, 分别对应域名ID和域名, 提交其中一个即可
        :param record_id 记录ID，必选
        """

        return self.post(' https://dnsapi.cn/Record.Info', dict(domain=domain, record_id=record_id))

    def record_set_status(self, domain, record_id, status):
        """设置解析记录的状态

        :param domain, 分别对应域名ID和域名, 提交其中一个即可
        :param record_id 记录ID，必选
        :param status {enable|disable} 新的状态，必选
        :return:
        """
        return self.post(' https://dnsapi.cn/Record.Status', dict(domain=domain, record_id=record_id, status=status))


class DnspodAPI(DnspodDNS):
    """统一接口"""
