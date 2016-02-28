from notes.models import Note, Comment

def get_subtree(root_note_id, result):
	n = Note.objects.get(pk = root_note_id)
	result.append(int(n.id))
	sub_notes = n.note_set.all()
	for item in sub_notes:
		result = get_subtree(item.id, result)
	return result