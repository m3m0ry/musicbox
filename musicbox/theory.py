from re import compile
from functools import total_ordering
from itertools import chain


@total_ordering
class Tone:
    tones = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    @staticmethod
    def all(starting='C'):
        index = Tone.tones.index(starting)
        for tone in chain(Tone.tones[index:] + Tone.tones[:index]):
            yield tone

    @staticmethod
    def number_to_tone(i):
        return Tone.tones[i]

    @staticmethod
    def tone_to_number(tone):
        return Tone.tones.index(tone)

    def __init__(self, tone):
        if isinstance(tone, str):
            self.number = self.tone_to_number(tone.upper())
        else:
            self.number = tone

    def __repr__(self):
        return f'Tone({self.number})'

    def __str__(self):
        return self.number_to_tone(self.number)

    def __lshift__(self, other):
        return Tone(self.number - other)

    def __rshift__(self, other):
        return Tone(self.number + other)

    def __lt__(self, other):
        return self.number < other.number

    def __eq__(self, other):
        return self.number == other.number

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, n):
        self._number = n % 12


@total_ordering
class Note:
    pattern = compile(r'([a-gA-G]#?)(\d)')

    @staticmethod
    def all(min_octave=4, max_octave=4):
        for octave in range(min_octave, max_octave + 1):
            for tone in Tone.tones:
                yield Note(f'{tone}{octave}')

    @staticmethod
    def range(low, high):
        note = low
        while note != high:
            yield note
            note = note >> 1
        yield high

    def __init__(self, note):
        m = self.pattern.match(note)
        self.tone = Tone(m.group(1))
        self.octave = int(m.group(2))

    def distance(self, other):
        return abs(self.midi - other.midi)

    def __repr__(self):
        return f'Note("{self.tone}{self.octave}")'

    def __str__(self):
        return f'{self.tone}{self.octave}'

    def __lshift__(self, other):
        tone = self.tone << other
        octave = self.octave
        if tone > self.tone:
            octave -= 1
        return Note(f'{tone}{octave}')

    def __rshift__(self, other):
        tone = self.tone >> other
        octave = self.octave
        if tone < self.tone:
            octave += 1
        return Note(f'{tone}{octave}')

    def __lt__(self, other):
        return self.octave < other.octave or self.tone < other.tone

    def __eq__(self, other):
        return self.tone == other.tone and self.octave == other.octave

    def __contains__(self, tone):
        return self.tone == tone

    @property
    def midi(self):
        return self.tone.number + self.octave * 12


@total_ordering
class Interval:
    intervals = {
        'P1': 0, 'd2': 0,
        'm2': 1, 'A1': 1,
        'M2': 2, 'd3': 2,
        'm3': 3, 'A2': 2,
        'M3': 4, 'd4': 4,
        'P4': 5, 'A3': 5,
        'd5': 6, 'A4': 6,
        'P5': 7, 'd6': 7,
        'm6': 8, 'A5': 8,
        'M6': 9, 'd7': 9,
        'm7': 10, 'A6': 10,
        'M7': 11, 'd8': 11,
        'P8': 12, 'A7': 12,
        'd1': -1}

    @staticmethod
    def from_tones(root, tone):
        return Interval((tone.number - root.number) % 12)

    def __init__(self, interval, octave=0):
        if isinstance(interval, str):
            interval = self.intervals[interval]
        self.interval = interval + 12 * octave

    def __str__(self):
        return str(self.interval)

    def __repr__(self):
        return f'Interval({self.interval % 12}, {self.interval // 12})'

    def __eq__(self, other):
        return self.interval == other.interval

    def __lt__(self, other):
        return self.interval < other.interval

    def __call__(self, a):
        if isinstance(a, Tone):
            return Tone(a.number + self.interval)
        else:
            return a >> self.interval


class Chord:
    recipes = {
        'maj':    ['P1', 'M3', 'P5'],
        'min':    ['P1', 'm3', 'P5'],
        'aug':    ['P1', 'M3', 'A5'],
        'dim':    ['P1', 'm3', 'd5'],
        'dom7':   ['P1', 'M3', 'P5', 'm7'],
        'min7':   ['P1', 'm3', 'P5', 'm7'],
        'maj7':   ['P1', 'M3', 'P5', 'M7'],
        'aug7':   ['P1', 'M3', 'A5', 'm7'],
        'dim7':   ['P1', 'm3', 'd5', 'd7'],
        'm7dim5': ['P1', 'm3', 'd5', 'm7'],
        'sus2':   ['P1', 'P5', 'P8', 'M2'],
        'sus4':   ['P1', 'P5', 'P8', 'P4'],
        'open5':  ['P1', 'P5', 'P8'],
    }
    aliases = {
        'M':      'maj',
        'm':      'min',
        '+':      'aug',
        '°':      'dim',
        '7':      'dom7',
        'm7':     'min7',
        'M7':     'maj7',
        '+7':     'aug7',
        '7aug5':  'aug7',
        '7#5':    'aug7',
        '°7':     'm7dim5',
        'ø7':     'm7dim5',
        'm7b5':   'm7dim5',
    }
    valid_types = list(recipes.keys()) + list(aliases.keys())

    @staticmethod
    def chord_from_tones(*tones):
        root = tones[0]
        intervals = []
        for t in tones:
            intervals.append(Interval.from_tones(root, t))
        for k, v in Chord.recipes.items():
            if intervals == [Interval(i) for i in v]:
                return Chord(root, k)
        raise ValueError(f'No Chord consist of {tones}')

    def __init__(self, root, chord_type='M'):
        if isinstance(root, str):
            self.root = Tone(root)
        else:
            self.root = root

        if chord_type in self.aliases:
            chord_type = self.aliases[chord_type]
        if chord_type not in self.recipes.keys():
            raise ValueError(f'Invalid chord type: {chord_type}')

        self.chord_type = chord_type
        self.tones = [Interval(i)(self.root) for i in self.recipes[chord_type]]

    def __repr__(self):
        return f'Chord("{self.root}", "{self.chord_type}")'

    def __str__(self):
        return f'{self.root}{self.chord_type}'

    def __eq__(self, other):
        if len(self.tones) != len(other.tones):
            return False
        else:
            return all(s == o for s, o in zip(self.tones, other.tones))


class Scale:
    scales = {
        'major': ['P1', 'M2', 'M3', 'P4', 'P5', 'M6', 'M7'],
        'minor': ['P1', 'M2', 'm3', 'P4', 'P5', 'm6', 'm7'],
        'natural_minor': ['P1', 'M2', 'm3', 'P4', 'P5', 'm6', 'm7'],
        'harmonic_minor': ['P1', 'M2', 'm3', 'P4', 'P5', 'm6', 'M7'],
        'melodic_minor': ['P1', 'M2', 'm3', 'P4', 'P5', 'M6', 'M7'],
        'major_pentatonic': ['P1', 'M2', 'M3', 'P5', 'M6'],
        'minor_pentatonic': ['P1', 'm3', 'P4', 'P5', 'm7'],
        'ionian': ['P1', 'M2', 'M3', 'P4', 'P5', 'M6', 'M7'],
        'dorian': ['P1', 'M2', 'm3', 'P4', 'P5', 'M6', 'm7'],
        'phrygian': ['P1', 'm2', 'm3', 'P4', 'P5', 'm6', 'm7'],
        'lydian': ['P1', 'M2', 'M3', 'A4', 'P5', 'M6', 'M7'],
        'mixolydian': ['P1', 'M2', 'M3', 'P4', 'P5', 'M6', 'm7'],
        'aeolian': ['P1', 'M2', 'm3', 'P4', 'P5', 'm6', 'm7'],
        'locrian': ['P1', 'm2', 'm3', 'P4', 'd5', 'm6', 'm7']
    }
    scale_types = list(scales.keys())

    def __init__(self, root, name):
        if isinstance(root, str):
            root = Tone(root)
        self.root = root
        self.name = name
        self.scale = self.scales[name]
        self.intervals = [Interval(i) for i in self.scale]
        self.tones = [i(self.root) for i in self.intervals]

    def __repr__(self):
        return f'Scale("{self.root}", "{self.name}")'

    def __str__(self):
        return ', '.join((str(t) for t in self.tones))

    def __eq__(self, other):
        return self.root == other.root and self.name == other.name

    def degree(self, deg):
        if isinstance(deg, str):
            deg = _roman_to_int(deg)
        deg -= 1
        root = self.tones[deg % len(self.tones)]
        third = self.tones[(deg + 2) % len(self.tones)]
        fifth = self.tones[(deg + 4) % len(self.tones)]
        return Chord.chord_from_tones(root, third, fifth)


def _roman_to_int(r):
    """ Convert a Roman numeral to an integer. """
    if not isinstance(r, str):
        raise TypeError(f'Expected string, got type(input)')
    r = r.upper()
    nums = {'M': 1000, 'D': 500, 'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1}
    integer = 0
    for i in range(len(r)):
        try:
            value = nums[r[i]]
            if i+1 < len(r) and nums[r[i + 1]] > value:
                integer -= value
            else:
                integer += value
        except KeyError:
            raise ValueError('Input is not a valid Roman numeral: %s' % r)
    return integer

