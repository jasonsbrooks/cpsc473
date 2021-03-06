'''
Note: by default, 100 ticks is a quarter note
thus:
8th: 50 ticks
16th: 25 ticks
32nd: 12.5 ticks

If 400 ticks is a quarter note
8th: 200
16th: 100
32nd: 50
'''

import midi, time, datetime

ed_to_midi_dic_c_maj = {
    1: midi.C_4,
    2: midi.D_4,
    3: midi.E_4,
    4: midi.F_4,
    5: midi.G_4,
    6: midi.A_4,
    7: midi.B_4,
    8: midi.C_5,
    9: midi.D_5,
    10: midi.E_5,
    11: midi.F_5,
    12: midi.G_5,
    13: midi.A_5,
    14: midi.B_5,
    15: midi.C_6,
    16: midi.D_6,
    17: midi.E_6,
    18: midi.F_6,
    19: midi.G_6,
    20: midi.A_6,
    21: midi.B_6
}


# given chord number, returns track object with one measure of that chord in quarter notes
# currently only gives notes for C major scale
def create_chord_measure(chord, a_train=False):
    """given chord number, returns track object with one 4/4 measure of that chord of quarter note durations
    
    Args:
        chord (int): 1-7 representing chord root in scale
        a_train (bool, optional): Defaults to False.  If True, uses chord progression to a_train, otherwise uses standard blues scales in C major
    
    Returns:
        Midi.Track: midi.Track object that represents chord progression in left hand of a piano.  Can be added directly to midi file for playback
    """
    track = midi.Track()
    midi_velocity = 80

    if not a_train:
        # default at 1 chord
        root = midi.C_3
        third = midi.E_3
        fifth = midi.G_3

        if chord == 4:
            root = midi.F_3
            third = midi.A_3
            fifth = midi.C_4
        elif chord == 5:
            root = midi.G_3
            third = midi.B_3
            fifth = midi.D_4

        for i in range(4):
            on1 = midi.NoteOnEvent(tick=0, velocity=midi_velocity, pitch=root)
            on2 = midi.NoteOnEvent(tick=0, velocity=midi_velocity, pitch=third)
            on3 = midi.NoteOnEvent(tick=0, velocity=midi_velocity, pitch=fifth)
            track.append(on1)
            track.append(on2)
            track.append(on3)

            midi_tick_dur = 133
            if i % 3 == 0:
                midi_tick_dur = 134

            off1 = midi.NoteOffEvent(tick=midi_tick_dur, pitch=root)
            off2 = midi.NoteOffEvent(tick=midi_tick_dur, pitch=third)
            off3 = midi.NoteOffEvent(tick=midi_tick_dur, pitch=fifth)
            track.append(off1)
            track.append(off2)
            track.append(off3)
    else:

        notes = []

        if chord == 1:  # C
            # default at 1 chord
            notes = [midi.C_3, midi.E_3, midi.G_3]
        elif chord == 2:  # D7b5
            notes = [midi.D_3, midi.Fs_3, midi.Gs_3]  #, midi.C_3]
        elif chord == 3:  # D_7
            notes = [midi.F_3, midi.Gs_3, midi.B_3]  #, midi.D_3]
        elif chord == 4:  # D7
            notes = [midi.D_3, midi.Fs_3, midi.A_3]  #, midi.C_3]
        elif chord == 5:  # F
            notes = [midi.F_3, midi.A_3, midi.C_3]
        elif chord == 6:  # G7
            notes = [midi.G_3, midi.B_3, midi.D_3]  #, midi.F_7]

        # for i in range(4):
        for note in notes:
            on1 = midi.NoteOnEvent(tick=0, velocity=midi_velocity, pitch=note)
            track.append(on1)

        # midi_tick_dur = 133
        # if i % 3 == 0:
        #     midi_tick_dur = 134

        midi_tick_dur = 533

        for note in notes:
            off1 = midi.NoteOffEvent(tick=midi_tick_dur, pitch=note)
            track.append(off1)

    return track


# given chromosome = (fitness, genotype)
# creates midi file titled the fitness level
def create_midi_file((fitness, genotype), chord_progression):
    """creates midi file from given chromosome and chord progression
    midi file is named based on fitness level and created timestamp.  File created in same directory as ga_midi.py
    
    Args:
        (fitness, genotype) (int, (int, int)[]): encoding for a chromsome.  Fitness is integer representing fitness.  Genotype is list of (pitch, duration) tuples representing each note to be played.
        chord_progression (: if True, uses chord progression to a_train, otherwise uses standard blues scales in C major
    
    Returns:
        void
    """
    # Instantiate a MIDI Pattern (contains a list of tracks)
    pattern = midi.Pattern()
    pattern.resolution = 400

    # Instantiate a MIDI Track (contains a list of MIDI events)
    track = midi.Track()
    # Append the track to the pattern
    pattern.append(track)

    # track.append(midi.TrackNameEvent(tick=0, name="boosbosjadioasjd"))

    for i, (ed, dur) in enumerate(genotype):
        # Instantiate a MIDI note on event, append it to the track
        midi_pitch = midi.B_6
        midi_velocity = 100
        if (ed == -1):  # i.e. a rest
            midi_velocity = 0
        else:
            midi_pitch = ed_to_midi_dic_c_maj[ed]
        on = midi.NoteOnEvent(tick=0, velocity=midi_velocity, pitch=midi_pitch)
        track.append(on)

        # Instantiate a MIDI note off event, append it to the track
        midi_tick_dur = dur * 50
        off = midi.NoteOffEvent(tick=midi_tick_dur, pitch=midi_pitch)
        track.append(off)

    # Add the end of track event, append it to the track
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    # Print out the pattern
    # print pattern

    # make 1-4-5 12 bar blues chord track
    track = midi.Track()
    # Append the track to the pattern
    pattern.append(track)

    for (root, dur) in chord_progression:  # Assumes chords all last 1 measure (32 durks duration)
        temp_track = create_chord_measure(root)
        track += temp_track

    # for _ in range(4):
    #     temp_track = create_chord_measure(1)
    #     track += temp_track
    # for _ in range(2):
    #     temp_track = create_chord_measure(4)
    #     track += temp_track
    # for _ in range(2):
    #     temp_track = create_chord_measure(1)
    #     track += temp_track
    # for _ in range(1):
    #     temp_track = create_chord_measure(5)
    #     track += temp_track
    # for _ in range(1):
    #     temp_track = create_chord_measure(4)
    #     track += temp_track
    # for _ in range(2):
    #     temp_track = create_chord_measure(1)
    #     track += temp_track

    # Add the end of track event, append it to the track
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)

    # Save the pattern to disk
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    midi.write_midifile(str(fitness) + "_" + st + ".mid", pattern)  # + str(detailed_fitness) + "_"
