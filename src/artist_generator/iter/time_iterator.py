from db import get_sessions,Song,Track,Note
from optparse import OptionParser

from song_iterator import SongIterator
from chord_iterator import ChordIterator

class TimeInstance(object):
    """
    TimeInstance: the set of chords "on" at a specific moment in time during a song
    """
    def __init__(self,time,chords):
        self.time = time
        self.chords = chords

    def __repr__(self):
        return "<TimeInstance len(chords)=%r, time=%r>" % (len(self.chords), self.time)

    def notes(self):
        """
        Flatten the set of chords
        @return: the Notes that comprise the different chords "on" at this moment in time
        """
        res = []
        for chord in self.chords:
            res += chord.notes
        return res

class TimeIterator(object):
    """
    Iterate through a song, TimeInstance by TimeInstance.
    """
    def __init__(self,song,durk_step):
        """
        Initialize a TimeIterator

        Args:
            song (Song): the song to iterate through
            durk_step (int): number of durks between TimeInstances
        """

        # durk_step is the step size between TimeInstances.
        self.durk_step = durk_step

        # construct the ChordIterator
        self.chord_iterator = ChordIterator(song)

        self.current_ts = None
        self.chords_to_consider = []

        # start at min_time. end at max_time
        all_notes = SongIterator(song).notes
        first_note = min(all_notes, key=lambda note: note.start + note.dur)
        self.time = first_note.start
        last_note = max(all_notes,key=lambda note: note.start + note.dur)
        self.max_time = last_note.start + last_note.dur

    def __iter__(self):
        return self

    def next(self):
        """
        Compute and return the next TimeInstance in this song

        Returns:
            TimeInstance: the next TimeInstance.
        """
        # past the end of the song
        if self.time >= self.max_time:
            raise StopIteration()
        else:
            chords = []

            # consider previous chords that might still be playing
            if self.current_ts:
                for chord in self.current_ts.chords:
                    if chord.on_at_time(self.time):
                        chords.append(chord)

            # grab next chords that need consideration
            next_chord = self.chord_iterator.next()
            self.chords_to_consider.append(next_chord)
            while next_chord.start <= self.time:
                next_chord = self.chord_iterator.next()
                self.chords_to_consider.append(next_chord)

            # consider these chords (as well as chords previously added to self.chords_to_consider)
            for chord in self.chords_to_consider:
                if chord.on_at_time(self.time):
                    chords.append(chord)

            self.current_ts = TimeInstance(self.time,chords)
            self.time += self.durk_step

            self.chords_to_consider = filter(lambda chord: self.time <= chord.end_time(),self.chords_to_consider)

            return self.current_ts

# when this file is run directly: used for debugging!
if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-d", "--durk-step", dest="durk_step", default=4, type="int")
    parser.add_option("-t", "--pool-size", dest="pool_size", default=8, type="int")
    parser.add_option("-u", "--username", dest="db_username", default="postgres")
    parser.add_option("-p", "--password", dest="db_password", default="postgres")
    parser.add_option("-b", "--db", dest="which_db", default=0, help="Which database # to draw from?")
    parser.add_option("-s", "--song", dest="which_song", default=1, help="Which song to debug with?")
    (options, args) = parser.parse_args()

    # get all db sessions
    sessions = get_sessions(options.pool_size,options.db_username,options.db_password)

    # grab the song from the database and just print out all timestamps.
    song = sessions[options.which_db].query(Song).get(options.which_song)
    for ts in TimeIterator(song,options.durk_step):
        print ts