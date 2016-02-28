from django import forms
from .models import Note, Comment

class PostNoteSubForm(forms.ModelForm):
	class Meta:
		model = Note
		fields = ('title', 'content_markdown',)

class PostNoteFullForm(forms.ModelForm):
	class Meta:
		model = Note
		fields = ('title', 'content_markdown', 'timestamp',)

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('content_markdown',)