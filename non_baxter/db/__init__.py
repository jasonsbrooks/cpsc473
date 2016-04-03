from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from song import Song
from track import Track
from note import Note

engine = create_engine('sqlite:////tmp/artist.db')
Session = sessionmaker(bind=engine)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
