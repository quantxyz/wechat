from django.contrib import admin
from .models import CustomValue, Userinfo, Orderinfo, TemplateMsg
# Register your models here.


class CustomValueAdmin(admin.ModelAdmin):
    fields = ['name', 'value']
    list_display = ('name', 'value')
    search_fields = ['name']


class UserinfoAdmin(admin.ModelAdmin):
    """
    is_tech(true,false)
    u_name(100), u_mobile(100), openid(100)
    """
    fields = ['u_name', 'u_mobile']
    list_display = ('u_name', 'u_mobile', 'u_openid', 'is_tech')
    search_fields = ['u_name']


class OrderinfoAdmin(admin.ModelAdmin):
    fields = ['order_type', 'c_name', 'c_mobile', 'c_time', 'tech_user', 'c_address', 'remark', 'ce_num', 'state']
    list_display = ('order_id', 'order_type', 'c_name', 'c_mobile', 'c_time', 'tech_user', 'ce_time', 'ce_num', 'state')
    search_fields = ['order_id', 'c_name', 'c_mobile']


class TemplateMsgAdmin(admin.ModelAdmin):
    """
    toUserName,fromUserName,createTime,msgType,event,status
    """
    fields = ['toUserName', 'createTime', 'msgType', 'event', 'status']
    list_display = ('toUserName', 'createTime', 'msgType', 'event', 'status')
    search_fields = ['msgType', 'event', 'status']

admin.site.register(CustomValue, CustomValueAdmin)
admin.site.register(Userinfo, UserinfoAdmin)
admin.site.register(Orderinfo, OrderinfoAdmin)
admin.site.register(TemplateMsg, TemplateMsgAdmin)
