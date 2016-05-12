# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jerry'
import sys
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from lxml import etree
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from .jssdk import Jssdk
from .wxser import WechatCallback
from .forms import CustomValueForm, OrderinfoForm
from .models import CustomValue, Userinfo, Orderinfo, TemplateMsg

import time
import logging
from urllib import urlencode

# Create your views here.

# connove
# AppID:appid
# AppSecret:AppSecret
appId = 'your_app_id'
appSecret = 'your_app_secret'
weixin_id = 'connove'
logger = logging.getLogger(__name__)

@csrf_exempt
def index(request):
    if request.method == 'GET':
        # if 'state' in request.GET:
        #     state = request.GET['state']
        #     code = request.GET['code']
        #     jssdk = Jssdk(appId, appSecret)
        #     if state == 'connovelistmyorderinfo':
        #         pass
        #     elif state == 'connovevieworder':
        #         openid = jssdk.getCurOpenId(code)
        #         uinfo = jssdk.getUserInfo(openid)
        #         next_url = request.path
        #         if int(uinfo['subscribe']) == 0:
        #             pass
        #         else:
        #             return HttpResponseRedirect(next_url)
        #
        # else:
        wxser = WechatCallback()
        return HttpResponse(wxser.valid(request))
    else:
        xmlstr = smart_str(request.body)
		logger.info('got the request body %s' % xmlstr)
        xml = etree.fromstring(xmlstr)
        ToUserName = xml.find('ToUserName').text
        FromUserName = xml.find('FromUserName').text
        CreateTime = xml.find('CreateTime').text
        MsgType = xml.find('MsgType').text 
        
        if MsgType == "text":
            Content = xml.find('Content').text
            logger.info('got the content %s' % Content)
            reply_xml = """
            <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%d</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[%s]]></Content>
            </xml>""" % (FromUserName, ToUserName, int(time.time()), Content + "  Hello world")

            return HttpResponse(reply_xml)
        elif MsgType == "event":
            logger.info('got the MsgType %s' % MsgType)
            event = xml.find("Event").text
            logger.info('got the event %s' % event)
            # 发送模板消息反馈
            if event == "TEMPLATESENDJOBFINISH":
                status = xml.find("Status").text
                #logger.info('got the status %s' % status)
                msg_time = datetime.fromtimestamp(int(CreateTime))
                tmsg = TemplateMsg(toUserName=ToUserName,
                                   fromUserName=FromUserName,
                                   createTime=msg_time,
                                   msgType=MsgType,
                                   event=event,
                                   status=status)
                tmsg.save()
            elif event == 'SCAN':
                scene_id = xml.find("EventKey").text
                logger.info('got the scene_id %s' % scene_id)
                o = get_object_or_404(Orderinfo, pk=int(scene_id))
                eval_url = "http://%s/wxorder/%d/evalo?" % (request.get_host(), o.id)
                params = {'uid': FromUserName}
                eval_url = eval_url + urlencode(params)
                eval_cont = '请您对技术人员%s进行评价，<a href="%s">前往评价</a>' \
                          % (o.tech_user.u_name, eval_url)
                reply_xml = """
                <xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%d</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>""" % (FromUserName, ToUserName, int(time.time()), eval_cont)

                return HttpResponse(reply_xml)
            elif event == 'subscribe':
                logger.info('got the event %s' % event)
                qrscene = xml.find("EventKey").text
                if qrscene != '':
                    scene_id = qrscene.split('_')[-1]
                    logger.info('got the scene_id %s' % scene_id)
                    o = get_object_or_404(Orderinfo, pk=int(scene_id))
                    eval_url = "http://%s/wxorder/%d/evalo?" % (request.get_host(), o.id)
                    params = {'uid': FromUserName}
                    eval_url = eval_url + urlencode(params)
                    eval_cont = '请您对技术人员%s进行评价，<a href="%s">前往评价</a>' \
                              % (o.tech_user.u_name, eval_url)
                else:
                    eval_cont = '欢迎您关注创恒应用，更多精彩期待您与我们互动。'
                reply_xml = """
                <xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%d</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                </xml>""" % (FromUserName, ToUserName, int(time.time()), eval_cont)

                return HttpResponse(reply_xml)
            else:
                return HttpResponse("connove") 


# jssdk
def hello(request):
    jssdk = Jssdk(appId, appSecret)
    url = request.build_absolute_uri()
    sign_package = jssdk.sign(url)
    return render(request, 'wxorder/hello.html', {'url': url, 'sign_package': sign_package, 'appId': appId})


# manager login
def manager_login(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        password = request.POST['password'].strip()
        # Validate the form: the captcha field will automatically
        # check the input
        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/wxorder/center')
                else:
                    msg = {
                        'type': 'warn',
                        'title': '登录失败',
                        'content': '您的帐号已被锁定，暂时无法登录',
                        'next_url': '/wxorder/login',
                        'btn_text': '返回'
                    }

                    return render(request, 'wxorder/msg.html', {'msg': msg})
            else:
                msg = {
                    'type': 'warn',
                    'title': '登录失败',
                    'content': '无效的登录信息: 用户名或密码错误',
                    'next_url': '/wxorder/login',
                    'btn_text': '返回'
                }
                return render(request, 'wxorder/msg.html', {'msg': msg})
        else:

            return render(request, 'wxorder/login.html',
                          {'u': username, 'p': password})
    # the request is not a http post, so display the login form
    # this scenario would most likely be a http get
    else:
        # No centext variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request, 'wxorder/login.html')


@login_required
def center(request):
    now = datetime.now()
    order_id_day = now.strftime('%Y%m%d')
    orders = Orderinfo.objects.filter(order_id__startswith=order_id_day)
    tech_users = Userinfo.objects.filter(is_tech=True)
    bus_types = CustomValue.objects.filter(name='bus_type')
    return render(request, 'wxorder/center.html', {'tody_o': orders,
                                                   'tusers': tech_users,
                                                   'btypes': bus_types})


@login_required
def list_customvalue(request):
    customvalues = CustomValue.objects.all()

    return render(request, 'wxorder/list_customvalue.html', {'cvlist': customvalues})


@csrf_exempt
@login_required
def add_customvalue(request):
    if request.method == 'POST':
        form = CustomValueForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponse('success')
        else:
            return HttpResponse('fail')


@csrf_exempt
@login_required
def edit_customvalue(request):
    if request.method == 'POST':
        id = request.POST['id']
        value = request.POST['value']
        if value and len(value) > 1:
            customvalue = get_object_or_404(CustomValue, pk=int(id))
            if customvalue is None:
                return HttpResponse('fail')
            num = CustomValue.objects.filter(pk=int(id)).update(value=value)
            if num == 1:
                return HttpResponse('success')
            else:
                return HttpResponse('fail')
        else:
            return HttpResponse('fail')


@login_required
def list_techuser(request):
    tech_users = Userinfo.objects.filter(is_tech=True)
    return render(request, 'wxorder/list_techuser.html', {'ters': tech_users})


@csrf_exempt
@login_required
def sync_techuser(request):
    if request.method == 'POST':
        jssdk = Jssdk(appId, appSecret)
        openids = jssdk.getTechUsers()
        if openids is None:
            return HttpResponse('fail')
        users = []
        for openid in openids:
            if Userinfo.objects.filter(u_openid=openid).values('id').exists():
                continue
            u_info = jssdk.getUserInfo(str(openid))
            if len(smart_str(u_info['remark'])) > 0:
                u_name = smart_str(u_info['remark'])
            else:
                u_name = smart_str(u_info['nickname'])
            u = Userinfo(u_name=u_name,
                         u_mobile='', is_tech=True,
                         u_openid=openid)
            users.append(u)
        if len(users) > 0:
            Userinfo.objects.bulk_create(users)
        return HttpResponse('success')


@csrf_exempt
@login_required
def edit_techuser(request):
    if request.method == 'POST':
        id = request.POST['id']
        name = request.POST['name']
        mobile = request.POST['mobile']
        if name and len(name) > 2 and (len(mobile) == 0 or len(mobile) == 11):
            u = get_object_or_404(Userinfo, pk=int(id))
            if u is None:
                return HttpResponse('fail')
            num = Userinfo.objects.filter(pk=int(id)).update(u_name=name,
                                                             u_mobile=mobile)
            if num == 1:
                return HttpResponse('success')
            else:
                return HttpResponse('fail')
        else:
            return HttpResponse('fail')


def sendTMsgOrNot(request, o):
    if o.state == 1:
        url = "http://%s/wxorder/%d/viewo" % (request.get_host(), o.id)
        c_info = "%s(%s)" % (o.c_name, o.c_mobile)
        payload = {
            "touser": o.tech_user.u_openid,
            "template_id": "JSyp6FLF1j1cqJLZRRV5n_ccDqlMYoTu_gfIx3RonOE",
            "url": url,
            "data": {
                "first": {
                    "value": "您有新的派单！",
                    "color": "#173177"
                },
                "keyword1": {
                    "value": o.order_id,
                    "color": "#173177"
                },
                "keyword2": {
                    "value": o.c_time,
                    "color": "#173177"
                },
                "keyword3": {
                    "value": c_info,
                    "color": "#173177"
                },
                "keyword4": {
                    "value": o.c_address,
                    "color": "#173177"
                },
                "keyword5": {
                    "value": o.tech_user.u_name,
                    "color": "#173177"
                },
                "remark": {
                    "value": "上门前请提前通知客户！",
                    "color": "#173177"
                }
            }
        }
        jssdk = Jssdk(appId, appSecret)
        result = jssdk.sendTemplateMsg(send_data=payload)
        if int(result['errcode']) != 0:
            result = jssdk.sendTemplateMsg(send_data=payload)
            if int(result['errcode']) != 0:
                msg = {
                    'type': 'warn',
                    'title': '发送派单微信通知失败',
                    'content': '发送给技术员的微信通知失败，请您稍后重试',
                    'next_url': '/wxorder/' + o.id + '/edito',
                    'btn_text': '重新派单'
                }
                return render(request, 'wxorder/msg.html', {'msg': msg})


@login_required
def add_orderinfo(request):
    """
    order_id state
    c_name c_mobile c_time
    c_address tech_user remark
    ce_num ce_remark ce_openid ce_time
    """
    te_users = Userinfo.objects.filter(is_tech=True)
    types = CustomValue.objects.filter(name='bus_type')
    if request.method == 'POST':
        c_time = ''
        tech_user = -1
        if 'c_time' in request.POST and request.POST['c_time']:
            c_time = request.POST['c_time']
        if 'tech_user' in request.POST and request.POST['tech_user']:
            tech_user = int(request.POST['tech_user'])
        form = OrderinfoForm(request.POST)
        if form.is_valid() and len(c_time) > 5 and tech_user > -1:
            o = form.save(commit=False)
            if tech_user > 0:
                o.state = 1
                o.tech_user_id = tech_user
            else:
                o.tech_user_id = None
            now = datetime.now()
            o.c_time = c_time
            o.order_id = now.strftime('%Y%m%d%H%M%S')
            o.save()

            sendTMsgOrNot(request, o)
            return HttpResponseRedirect(reverse('wxorder:list_orderinfo'))
        else:
            return render(request, 'wxorder/add_orderinfo.html', {'form': form,
                                                                  'tus': te_users,
                                                                  'types': types})
    # 'c_name', 'c_mobile', 'c_time', 'c_address', 'tech_user', 'remark'
    return render(request, 'wxorder/add_orderinfo.html', {'tus': te_users,
                                                          'types': types})


@login_required
def list_orderinfo(request):
    orderinfos = Orderinfo.objects.all()
    ze_orders = orderinfos.filter(state=0)
    fi_orders = orderinfos.filter(state=1)
    se_orders = orderinfos.filter(state=2)
    return render(request, 'wxorder/list_orderinfo.html', {'z': ze_orders,
                                                           'f': fi_orders,
                                                           's': se_orders})


def view_orderinfo(request, oid):
    # next_url = request.path
    # print next_url
    # host = request.get_host()
    # print host
    o = get_object_or_404(Orderinfo, pk=oid)
    if o.qcode.find('https') == -1:
        jssdk = Jssdk(appId, appSecret)
        o.qcode = jssdk.getQcodeUrl(oid)
        o.save()
    return render(request, 'wxorder/view_orderinfo.html', {'o': o})


@login_required
def edit_orderinfo(request, oid):
    """
    order_id state
    c_name c_mobile c_time
    c_address tech_user remark
    ce_num ce_remark ce_openid ce_time
    """
    te_users = Userinfo.objects.filter(is_tech=True)
    types = CustomValue.objects.filter(name='bus_type')
    o = get_object_or_404(Orderinfo, pk=oid)
    if request.method == 'POST':
        c_time = ''
        tech_user = -1
        if 'c_time' in request.POST and request.POST['c_time']:
            c_time = request.POST['c_time']
        if 'tech_user' in request.POST and request.POST['tech_user']:
            tech_user = int(request.POST['tech_user'])
        form = OrderinfoForm(data=request.POST, instance=o)
        if form.is_valid() and len(c_time) > 5 and tech_user > -1:
            o = form.save(commit=False)
            if tech_user > 0:
                o.state = 1
                o.tech_user_id = tech_user
            else:
                o.tech_user_id = None
            o.c_time = c_time
            o.save()
            sendTMsgOrNot(request, o)
            return HttpResponseRedirect(reverse('wxorder:list_orderinfo'))
        else:
            return render(request, 'wxorder/edit_orderinfo.html', {'form': form,
                                                                   'o': o,
                                                                   'tus': te_users,
                                                                   'types': types})
    # 'c_name', 'c_mobile', 'c_time', 'c_address', 'tech_user', 'remark'
    return render(request, 'wxorder/edit_orderinfo.html', {'tus': te_users,
                                                           'types': types,
                                                           'o': o})


def eval_orderinfo(request, oid):
    """
    order_id state qcode order_type
    c_name c_mobile c_time
    c_address tech_user remark
    ce_num ce_remark ce_openid ce_time
    """
    o = get_object_or_404(Orderinfo, pk=oid)
    if o.state == 2:
        msg = {
            'type': 'success',
            'title': '该派单已评价',
            'content': '该服务已评价，谢谢您的关注！',
            'next_url': '#',
            'btn_text': '去商城逛逛'
        }
        return render(request, 'wxorder/msg.html', {'msg': msg})
    elif o.state == 0:
        msg = {
            'type': 'warn',
            'title': '该派单还未生效',
            'content': '该派单还未生效或已作废，谢谢您的关注！',
            'next_url': '#',
            'btn_text': '去商城逛逛'
        }
        return render(request, 'wxorder/msg.html', {'msg': msg})
    if request.method == 'GET':
        if 'uid' in request.GET and request.GET['uid']:
            openid = request.GET['uid']
            t_openid = o.tech_user.u_openid
            if t_openid == openid:
                msg = {
                    'type': 'warn',
                    'title': '非法操作',
                    'content': '请我们的客户对我们的服务进行评价',
                    'next_url': '#',
                    'btn_text': '去商城逛逛'
                }
                return render(request, 'wxorder/msg.html', {'msg': msg})
            return render(request, 'wxorder/eval_orderinfo.html',
                          {'o': o, 'openid': openid})
        else:
            msg = {
                'type': 'warn',
                'title': '非法操作',
                'content': '请在微信客户端用扫一扫访问该页面',
                'next_url': '#',
                'btn_text': '去商城逛逛'
            }
            return render(request, 'wxorder/msg.html', {'msg': msg})
    elif request.method == 'POST':
        # ce_num 0：满意 1：一般 2：不满意
        ce_openid = request.POST['ce_openid']
        ce_num = int(request.POST['ce_num'])
        ce_remark = request.POST['ce_remark']
        t_openid = o.tech_user.u_openid
        if ce_openid and ce_num in [0, 1, 2] and ce_openid !=t_openid:
            o.ce_num = ce_num
            o.ce_remark = ce_remark
            o.ce_openid = ce_openid
            o.ce_time = datetime.now()
            o.state = 2
            o.save()
            msg = {
                'type': 'success',
                'title': '评价成功',
                'content': '谢谢您的评价，我们会继续努力，为您提供更好的服务！',
                'next_url': '#',
                'btn_text': '去商城逛逛'
            }
            return render(request, 'wxorder/msg.html', {'msg': msg})
        else:
            msg = {
                'type': 'warn',
                'title': '评价失败',
                'content': '请在微信客户端用扫一扫访问该页面',
                'next_url': '#',
                'btn_text': '去商城逛逛'
            }
            return render(request, 'wxorder/msg.html', {'msg': msg})
