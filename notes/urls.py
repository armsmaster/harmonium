from django.conf.urls import url

from . import views

app_name = 'notes'

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^(?P<note_id>[0-9]+)/$', views.note, name='note'),
	url(r'^note_edit/(?P<note_id>[0-9]+)/$', views.note_edit, name='note_edit'),
	url(r'^note_delete/(?P<note_id>[0-9]+)/$', views.note_delete, name='note_delete'),
	url(r'^login/$', 'django.contrib.auth.views.login'),
	url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/notes/'}),
	url(r'^my_shares/$', views.my_shares, name='my_shares'),
	url(r'^others_shares/$', views.others_shares, name='others_shares'),
	url(r'^comments_feed/$', views.comments_feed, name='comments_feed'),
]