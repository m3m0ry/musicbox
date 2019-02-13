import musicbox.theory as th
import musicbox.box as box

import random


def setting():
    out = dict()
    out['root'] = random.choice(list(th.Tone.all()))
    scale_types = ['major']  # TODO select all scales
    out['scale_type'] = random.choice(scale_types)
    out['scale'] = th.Scale(out['root'], out['scale_type'])
    return out


def main():
    print(setting())


if __name__ == '__main__':
    main()
