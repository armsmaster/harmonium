from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404

from .models import Note, Comment, Share
from .forms import PostNoteSubForm, PostNoteFullForm, CommentForm
from .algos import get_subtree

# Create your views here.
@login_required
def index(request):
	try:
		notes = Note.objects.filter(parent_note__isnull = True, user = request.user)
		if request.method == "POST":
			f = PostNoteFullForm(request.POST)
			ff = 'ff'
			if f.is_valid():
				f.user = request.user
				uu = 'uu'
				n = f.save(commit=False)
				n.user = request.user
				n.save()
				notes = Note.objects.filter(parent_note__isnull = True, user = request.user)
		form = PostNoteFullForm
	except:
		#raise Http404("WTF")
		return HttpResponseRedirect("/notes/")
	return render(request, 'notes/index.html', {'notes': notes, 'form': form })

@login_required
def note_delete(request, note_id):
	try:
		note = Note.objects.get(pk=note_id)
		
		if note.user.id != request.user.id:
			return HttpResponseRedirect("/notes/" + str(note_id))
		
		had_parent = note.has_parent()
		parent_id = 0
		if had_parent:
			parent_id = note.parent_note.id
		note.delete()
	except:
		#raise Http404("WTF")
		return HttpResponseRedirect("/notes/")
	if had_parent:
		return HttpResponseRedirect("/notes/" + str(parent_id))
	else:
		return HttpResponseRedirect("/notes/")

@login_required
def note_edit(request, note_id):
	try:
		note = Note.objects.get(pk=note_id)
		
		if note.user.id != request.user.id:
			return HttpResponseRedirect("/notes/" + str(note_id))
		
		if request.method == "POST":
			f = PostNoteSubForm(request.POST, instance = note)
			n = f.save(commit=True)
			n.parent_note = None
			if int(request.POST['parent_note']) > 0:
				np = Note.objects.get(pk=request.POST['parent_note'])
				n.parent_note = np
			n.save()
			return HttpResponseRedirect("/notes/" + str(note.id))
		form = PostNoteSubForm(instance = note)
		
		possible_parents = Note.objects.filter(user=request.user)
		subnotes = []
		excluded_parents = get_subtree(note.id, subnotes)
		temp = []
		for ppp in possible_parents:
			if int(ppp.id) not in excluded_parents:
				temp.append(ppp)
		parents = []
		parents = temp
	except:
		#raise Http404("WTF")
		return HttpResponseRedirect("/notes/")
	return render(request, 'notes/note_edit.html', { 'note': note, 'form': form, 'parents': parents, 'excluded_parents': possible_parents })

@login_required
def my_shares(request):
	try:
		all_shares = Share.objects.filter(owner=request.user)
		all_notes = Note.objects.filter(user=request.user)
		all_users = User.objects.exclude(pk=request.user.id)
		if request.method == "POST":
			do_insert = True
			if int(request.POST['share_note']) < 0:
				do_insert = False
			if int(request.POST['share_user']) < 0:
				do_insert = False
			n = Note.objects.get(pk = int(request.POST['share_note']))
			u = User.objects.get(pk = int(request.POST['share_user']))
			if do_insert:
				x = Share.objects.filter(owner=request.user, note=n, user=u)
				if x.count() > 0:
					do_insert = False
			if do_insert:
				sh = Share(owner=request.user, user=u, note=n)
				sh.save()
				all_shares = Share.objects.filter(owner=request.user)
	except:
		return HttpResponseRedirect("/notes/")
	return render(request, 'notes/my_shares.html', { 'all_shares': all_shares, 'all_notes': all_notes, 'all_users': all_users })

@login_required
def others_shares(request):
	try:
		all_shares = Share.objects.filter(user=request.user)
	except:
		return HttpResponseRedirect("/notes/")
	return render(request, 'notes/others_shares.html', { 'all_shares': all_shares })

@login_required
def comments_feed(request):
	try:
		user_notes = Note.objects.filter(user=request.user)
		shared_notes = Share.objects.filter(user=request.user)
		
		all_comments = []
		for n in user_notes:
			for c in n.comment_set.all():
				all_comments.append(c)
		
		for s in shared_notes:
			for c in s.note.comment_set.all():
				all_comments.append(c)
				
		all_comments=sorted(all_comments, key=lambda c: c.timestamp, reverse=True)
	except:
		return HttpResponseRedirect("/notes/")
		x = 'x'
	return render(request, 'notes/comments_feed.html', { 'all_comments': all_comments })
	
@login_required
def note(request, note_id):
	try:
		note = Note.objects.get(pk=note_id)
		s = Share.objects.filter(note=note, user=request.user)
		
		auth_ok = False
		
		if note.user.id == request.user.id:
			auth_ok = True
		
		if s.count() > 0:
			auth_ok = True
		
		if not auth_ok:
			return HttpResponseRedirect("/notes/")
		
		subnotes = []
		for n in note.note_set.all():
			if n.user == request.user:
				subnotes.append(n)
			if Share.objects.filter(note=n, user=request.user):
				subnotes.append(n)
		
		if request.method == "POST":
			if request.POST['form_type'] == 'note':
				f = PostNoteSubForm(request.POST)
				n = f.save(commit=False)
				n.user = request.user
				n.parent_note = note
				n.save()
				subnotes.append(n)
			if request.POST['form_type'] == 'comment':
				f = CommentForm(request.POST)
				c = f.save(commit=False)
				c.user = request.user
				c.note = Note.objects.get(pk=int(request.POST['note_id']))
				c.save()
		form = PostNoteSubForm()
		form_comment = CommentForm()
	except:
		#raise Http404("WTF")
		return HttpResponseRedirect("/notes/")
	return render(request, 'notes/note.html', { 'note': note, 'form': form, 'form_comment': form_comment, 'subnotes': subnotes })