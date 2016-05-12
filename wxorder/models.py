#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Manager(models.Model):
    m_user = models.OneToOneField(User)
    m_openid = models.CharField(max_length=50, verbose_name='openid', blank=True)

    def __unicode__(self):
        return self.m_user.username


class Userinfo(models.Model):
    """
    is_tech(true,false)
    u_name(100), u_mobile(100), openid(100)
    """
    is_tech = models.BooleanField(verbose_name='技术人员？', default=False)
    u_name = models.CharField(max_length=100, verbose_name='姓名')
    u_mobile = models.CharField(max_length=11, verbose_name='手机')
    u_openid = models.CharField(max_length=50, verbose_name='openid',
                                blank=True)

    def __unicode__(self):
        return self.u_name


class CustomValue(models.Model):
    name = models.CharField(max_length=30, verbose_name='变量类型', default='')
    value = models.CharField(max_length=50, verbose_name='变量值', default='')

    def __unicode__(self):
        return self.value


class Orderinfo(models.Model):
    """
    state 订单处理状态:0:未指定技术员 1：待评价（生成二维码） 2：已评价（查看订单服务结果）
    ce_num 0：满意 1：一般 2：不满意
    """
    order_id = models.CharField(max_length=14, verbose_name='订单编号')
    c_name = models.CharField(max_length=50, verbose_name='客户姓名')
    c_mobile = models.CharField(max_length=11, verbose_name='客户手机号码')
    c_time = models.DateTimeField(verbose_name='预计服务时间')
    c_address = models.CharField(max_length=100, verbose_name='客户地址')
    tech_user = models.ForeignKey(Userinfo, verbose_name='所属技术员', blank=True, null=True)
    order_type = models.ForeignKey(CustomValue, verbose_name='业务类型', related_name='bus_type', default=1)
    remark = models.CharField(max_length=200, verbose_name='备注')
    state = models.SmallIntegerField(verbose_name='订单状态', default=0)
    ce_num = models.SmallIntegerField(verbose_name='客户评价', default=0)
    ce_remark = models.CharField(max_length=255, verbose_name='客户评价备注')
    ce_openid = models.CharField(max_length=50, verbose_name='客户openid')
    ce_time = models.DateTimeField(verbose_name='客户评价时间', auto_now_add=True)
    qcode = models.CharField(max_length=200, verbose_name='二维码', default='/static/wxorder/img/qrcode.png')


class TemplateMsg(models.Model):
    toUserName = models.CharField(max_length=50, verbose_name='接收方')
    fromUserName = models.CharField(max_length=50, verbose_name='发送方')
    createTime = models.DateTimeField(verbose_name='创建时间')
    msgType = models.CharField(max_length=20, verbose_name='消息类型')
    event = models.CharField(max_length=30,verbose_name='模板消息发送结束')
    # 1 success 2 failed:user block 3 failed: system failed
    status = models.CharField(max_length=50, verbose_name='发送状态')