from django.conf.urls import url

from . import views
app_name = 'wxorder'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^hello$', views.hello, name='hello'),
    url(r'^login$', views.manager_login, name='login'),
    url(r'^center$', views.center, name='center'),
    url(r'^list_customvalue$', views.list_customvalue, name='list_customvalue'),
    url(r'^add_customvalue$', views.add_customvalue, name='add_customvalue'),
    url(r'^edit_customvalue$', views.edit_customvalue, name='edit_customvalue'),
    url(r'^list_techuser$', views.list_techuser, name='list_techuser'),
    url(r'^sync_techuser$', views.sync_techuser, name='sync_techuser'),
    url(r'^edit_techuser$', views.edit_techuser, name='edit_techuser'),
    url(r'^add_orderinfo$', views.add_orderinfo, name='add_orderinfo'),
    url(r'^list_orderinfo$', views.list_orderinfo, name='list_orderinfo'),
    url(r'^(?P<oid>[0-9]+)/viewo$', views.view_orderinfo, name='view_orderinfo'),
    url(r'^(?P<oid>[0-9]+)/edito$', views.edit_orderinfo, name='edit_orderinfo'),
    url(r'^(?P<oid>[0-9]+)/evalo$', views.eval_orderinfo, name='eval_orderinfo'),
]
