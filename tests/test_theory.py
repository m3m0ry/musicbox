from musicbox.theory import Tone, Note, Interval, Scale, Chord


def test_tone_init():
    tone1 = Tone(0)
    tone2 = Tone('C')
    assert tone1 == tone2
    assert len(list(Tone.all())) == 12
    assert len(list(Tone.all('A'))) == 12
    assert eval(repr(tone1)) == tone1


def test_tone_shift():
    tone1 = Tone(0)
    tone2 = Tone('C')
    tone1 = tone1 >> 1
    assert tone1 == Tone('C#')
    assert tone2 == tone1 << 1
    assert tone2 << 1 == Tone('B')


def test_tone_comparison():
    tone1 = Tone('C')
    tone2 = Tone('D')
    assert tone1 < tone2
    assert tone1 != tone2
    assert not tone1 > tone2


def test_note_init():
    note1 = Note('C#4')
    assert eval(repr(note1)) == note1
    assert str(note1) == 'C#4'
    assert note1.tone == Tone('C#')
    assert note1.octave == 4
    assert len(list(Note.all())) == 12
    assert len(list(Note.all(1, 4))) == 4 * 12
    assert Note('C4').midi == 48


def test_note_shift():
    note1 = Note('C4')
    note2 = note1 << 1
    assert note2 == Note('B3')
    note2 = note2 >> 1
    assert note2 == note1


def test_note_comparison():
    note1 = Note('C4')
    note2 = Note('C3')
    note3 = Note('A4')
    assert note2 < note1
    assert note2 != note1
    assert note1 < note3


def test_interval_init():
    interval1 = Interval(0)
    interval2 = Interval('P1')
    interval3 = Interval('P5', 2)
    assert interval1 == interval2
    assert eval(repr(interval1)) == interval1
    assert str(interval1) == "0"
    assert interval3.interval == 2 * 12 + 7


def test_scale_init():
    scale1 = Scale('A', 'minor')
    scale2 = Scale('C', 'major')
    assert eval(repr(scale1)) == scale1
    assert scale1.tones == scale2.tones[5:] + scale2.tones[:5]


def test_chord_init():
    chord = Chord('C', 'maj')
    print(chord.tones)
