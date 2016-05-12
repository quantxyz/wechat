# !/usr/bin/env python
# -*- coding: utf-8 -*-
from django.http import HttpResponse
import hashlib


class WechatCallback:

    def __init__(self):
        self.token = 'yourtokenlongtokenittoken'

    def valid(self, request):
        if self.check_signature(request.GET):
            return request.GET.get('echostr')
        else:
            return 'error'

    def check_signature(self, pams):
        if not self.token:
            return HttpResponse('TOKEN is not defined!')

        signature = pams.get('signature', '')
        timestamp = pams.get('timestamp', '')
        nonce = pams.get('nonce', '')
        tmparr = [self.token, timestamp, nonce]
        tmparr.sort()
        string = ''.join(tmparr)
        string = hashlib.sha1(string).hexdigest()
        print signature
        print string
        return signature == string
