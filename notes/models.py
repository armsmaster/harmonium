from django.db import models

from datetime import datetime
from markdown import markdown

# Create your models here.
class Note(models.Model):
	user = models.ForeignKey('auth.User')
	parent_note = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
	title = models.CharField(max_length=200)
	content = models.TextField(default='', null=True, blank=True)
	content_markdown = models.TextField(default='', null=True, blank=True)
	content_html = models.TextField(default='', editable = False, null=True, blank=True)
	timestamp = models.DateTimeField(default=datetime.now)
	def __str__(self):
		return self.title[:32]
	def has_parent(self):
		return not (self.parent_note == None)
	def save(self):
		self.content_html = markdown(self.content_markdown)
		super(Note, self).save()

class Comment(models.Model):
	user = models.ForeignKey('auth.User')
	content = models.TextField()
	content_markdown = models.TextField(default='', null=True, blank=True)
	content_html = models.TextField(default='', editable = False, null=True, blank=True)
	note = models.ForeignKey(Note, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(default=datetime.now)
	def __str__(self):
		return str(self.id) + self.content[0:32]
	def save(self):
		self.content_html = markdown(self.content_markdown)
		super(Comment, self).save()

class Share(models.Model):
	note = models.ForeignKey(Note, on_delete=models.CASCADE)
	owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='own_notes')
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='others_notes')