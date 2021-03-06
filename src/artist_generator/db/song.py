from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from . import Base

class Song(Base):
    """
    A Song with the following properties:
    """
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    """int: primary key"""

    title = Column(String, nullable=False)
    """str: String representing title of Song"""

    ppqn = Column(Integer, nullable=False)
    """int: Integer representing "pulses per quarter note" (i.e. 96 ticks/ quarter note)"""

    tracks = relationship("Track")
    """list of Track objects that constitute the song"""
    
    analyzed = Column(Boolean, nullable=True)
    """True once this song has been analyzed, NULL otherwise"""

    def __repr__(self):
        return "Song(title=%r, ppqn=%r, len(tracks)=%r, analyzed=%r)" % \
            (self.title, self.ppqn, len(self.tracks), self.analyzed)
