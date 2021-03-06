from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from . import Base

class Note(Base):
    """
    A Note represents a line of note in a track with the following properties:
    """

    __tablename__ = 'note'

    id = Column(Integer, primary_key=True)
    """int: primary key"""

    pitch = Column(Integer, nullable=False)
    """int: Integer from 0-127 representing note pitch

            Note: Defaults at 60 (C3)

            Note: -1 represents a "rest note" """

    iso_pitch = Column(String(length=8), nullable=True)
    """str: ISO representation of the note's pitch (eg. C, G, D, A E, B, F# ...)"""

    dur = Column(Integer, nullable=False)
    """int: Integer where 1 === 32nd note and 32 === whole note.  Call this unit "durks"""

    start = Column(Integer, nullable=False)
    """int: Integer representing start time of note relative to Song in "durk" units (see dur)"""

    end = Column(Integer, nullable=False)
    """int: Integer representing end time of note relative to Song in "durk" units (see dur)"""

    tick_dur = Column(Integer, nullable=False)
    """int: Integer representing duration of note in ticks

            Note: will be -1 for rest (no meaning)"""

    start_tick = Column(Integer, nullable=False)
    """int: Integer representing start time of note relative to Song (i.e. 0 is beginning of song) in tick units

            Note: NOT relative to Track object, relative to Song object!

            Note: will be -1 for rest (no meaning)"""

    measure = Column(Integer, nullable=False)
    """int: Integer representing measure of Song note is contained within
            Note: 0 is the first measure of a Song"""

    track_id = Column(Integer, ForeignKey('track.id'))
    """int: id of the Track to which this Note belongs"""


    track = relationship("Track", back_populates="notes")
    """Track: the track to which this Note belongs"""

    root = Column(Integer, nullable=True)
    """int: root of chord that this note start being played within

            Note: ...-2 -1  0  1  2  3  4  5  6  7  8  9 10 11 12 ...

                  ... Ab Eb Bb F  C  G  D  A  E  B  F# C# G# D# A#..."""

    iso_root = Column(String(length=8), nullable=True)
    """str: ISO representation of the root of the chord."""

    roman = Column(Integer, nullable=True)
    """int: the Roman Numeral representation of this Note's chord root"""

    def __repr__(self):
        return "note(pitch=%r, iso_pitch=%r, dur=%r, start=%r, tick_dur=%r, start_tick=%r, measure=%r, root=%r, iso_root=%r)" % \
            (self.pitch, self.iso_pitch, self.dur, self.start, self.tick_dur, self.start_tick, self.measure, self.root,self.iso_root)
