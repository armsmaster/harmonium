from django import template
from django.contrib.auth.models import User

from notes.models import Note, Comment, Share

register = template.Library()

def cut(value, arg):
	"""Removes all values of arg from the given string"""
	return value.replace(arg, '')
	
@register.simple_tag(name='access_granted')
def access_granted(n_id, u_id):
	n = Note.objects.get(pk=int(n_id))
	n = User.objects.get(pk=int(u_id))
	if n.user == u:
		return True
	if Share.objects.filter(user=u,note=n).count() != 0:
		return True
	return False