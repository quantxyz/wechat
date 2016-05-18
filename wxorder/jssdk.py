# coding=utf-8
__author__ = 'Jerry'
import json
import time
import requests
import random
import string
import hashlib

class Jssdk:
    def __init__(self, appId, appSecret):
        self.appId = appId
        self.appSecret = appSecret

        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.getJsApiTicket(),
            'timestamp': self.__create_timestamp(),
            'url': ''
        }

    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15))

    def __create_timestamp(self):
        return int(time.time())

    def sign(self, url):
        self.ret['url'] = url
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret

    def getAccessToken(self):
        json_file = open('access_token.json')
        data = json.load(json_file)
        json_file.close()
        access_token = data['access_token']
        
        if data['expire_time'] < time.time():
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" %\
                  (self.appId, self.appSecret)
            response = requests.get(url)
            access_token = json.loads(response.text)['access_token']
            data['access_token'] = access_token
            data['expire_time'] = int(time.time()) + 7000
            json_file = open('access_token.json', 'w')
            json_file.write(json.dumps(data))
            json_file.close()
        return access_token

    def getJsApiTicket(self):
        json_file = open('jsapi_ticket.json')
        data = json.load(json_file)
        json_file.close()
        jsapi_ticket = data['jsapi_ticket']
        if data['expire_time'] < time.time():
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi&access_token=%s" %\
                  (self.getAccessToken())
            response = requests.get(url)
            jsapi_ticket = json.loads(response.text)['ticket']
            data['jsapi_ticket'] = jsapi_ticket
            data['expire_time'] = int(time.time()) + 7000
            json_file = open('jsapi_ticket.json', 'w')
            json_file.write(json.dumps(data))
            json_file.close()
        return jsapi_ticket

    def getTechUsers(self):
        url = "https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token=%s" % (self.getAccessToken())
        payload = {'tagid': self.getTagId(), 'next_openid': ''}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        print data
        openids = data['data']['openid']
        return openids

    def getTagId(self):
        set_data = open('set_data.json')
        data = json.load(set_data)
        set_data.close()
        if data['tagid']:
            return data['tagid']
        else:
            return 101

    def getUserInfo(self, openid):
        # https://api.weixin.qq.com/cgi-bin/user/info?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
        url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" \
              % (self.getAccessToken(), openid)
        response = requests.get(url)
        return response.json()

    def getCurOpenId(self, code):
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" \
              % (self.appId, self.appSecret, code)
        response = requests.get(url)
        data = response.json()
        openid = data['openid']
        return openid

    def getQcodeUrl(self, oid):
        url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s" % (self.getAccessToken())
        payload = {'expire_seconds': 2591999, 'action_name': 'QR_SCENE', 'action_info': {"scene": {"scene_id": oid}}}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        ticket = data['ticket']
        # http://weixin.qq.com/q/zUipXRjlo7zaLJROUmaT
        # print data['url']
        url_qcode = "https://mp.weixin.qq.com/cgi-bin/showqrcode?"
        params = {'ticket': ticket}
        from urllib import urlencode
        # Content-Type:image/jpg
        return url_qcode + urlencode(params)

    def sendTemplateMsg(self, send_data):
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s'\
              % (self.getAccessToken())
        # send_data = {
        #     "touser":'oV9A7sx6y838j3rSFfgECitC-zbE',
        #     "template_id":"JSyp6FLF1j1cqJLZRRV5n_ccDqlMYoTu_gfIx3RonOE",
        #     "url":'http://wx.domain.com',
        #     "data":{
        #            "first": {
        #                "value":"请您对我们工作人员的服务评价！",
        #                "color":"#173177"
        #            },
        #            "keyword1":{
        #                "value":'20160506220527',
        #                "color":"#173177"
        #            },
        #            "keyword2": {
        #                "value":'2016-05-07 13:00',
        #                "color":"#173177"
        #            },
        #            "keyword3": {
        #                "value":'刘XXX',
        #                "color":"#173177"
        #            },
        #            "keyword4": {
        #                    "value":'南明区遵义路万象国际Ｃ座18-16号',
        #                    "color":"#173177"
        #                },
        #            "keyword5": {
        #                    "value":'钟小鸣[工号:003]',
        #                    "color":"#173177"
        #                },
        #            "remark":{
        #                "value":"以上是您的服务信息，请您对我们员工的服务做出评价，谢谢！",
        #                "color":"#173177"
        #            }
        #     }
        # }
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(send_data), headers=headers)
        data = response.json()
        return data

    def getTemplate(self):
        url = 'https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token=%s' \
              % (self.getAccessToken())
        resp = requests.get(url)
        data = resp.json()
        return data
