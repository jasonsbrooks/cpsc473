import rospy
import baxter_artist.msg

QUEUE_SIZE = 100
BPM = 60

# convert BPM to DURKS_PER_SECOND
DURKS_PER_SECOND = 8.0 * float(BPM) / 60.0
SECONDS_PER_DURK = 1.0 / float(DURKS_PER_SECOND)

class NotePublisher(object):
    def __init__(self):
        rospy.loginfo("Initializing NotePublisher")
        self.publisher = rospy.Publisher('baxter_artist_notes', baxter_artist.msg.Note, queue_size=QUEUE_SIZE)
        
        # need to sleep between creating Publisher and publishing to it.
        rospy.loginfo("Sleeping...")
        rospy.sleep(5)

    def pub_note(self,pitch,starttime):
        
        # construct the note message
        msg = baxter_artist.msg.Note()
        msg.starttime = starttime
        msg.pitch = pitch 

        rospy.loginfo("publish - pitch: " + str(msg.pitch))
        
        # publish the message
        self.publisher.publish(msg)

    def pub_notes(self,notes):
        # wait 2 seconds before starting the piece
        piece_starttime = rospy.Time.now() + rospy.Duration.from_sec(2)

        # when the next note should start
        note_starttime = piece_starttime

        for note in notes:
            pitch = note[0]
            dur = note[1]

            # send the note message
            self.pub_note(pitch,note_starttime)
            note_starttime += rospy.Duration.from_sec(dur * SECONDS_PER_DURK)
