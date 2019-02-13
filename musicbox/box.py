from musicbox.theory import Note


class Box:
    pass


class GI30(Box):
    notes = ['E6', 'D6', 'D4', 'C4', 'B3', 'A3', 'G3', 'D3', 'C3']
    notes = [Note(n) for n in notes]
    notes.extend(Note.range(Note('E4'), Note('C6')))


