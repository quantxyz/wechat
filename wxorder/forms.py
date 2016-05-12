#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jerry'
from django import forms
from .models import CustomValue, Orderinfo


class CustomValueForm(forms.ModelForm):
    class Meta:
        model = CustomValue
        """
        name(30), value(50)
        """
        fields = ('name', 'value')


class OrderinfoForm(forms.ModelForm):
    class Meta:
        model = Orderinfo
        """
        order_type order_id c_name c_mobile c_time
        c_address tech_user remark state
        ce_num ce_remark ce_openid ce_time
        """
        fields = ('order_type', 'c_name', 'c_mobile', 'c_address', 'remark')
