import os

if os.environ.get("ROS_ROOT"):
    import rospy,rospkg

    ROS_ENABLED = True
    """Are we running in a ROS environment?
    """

    # calculate directory location information
    _rospack = rospkg.RosPack()

    ARTIST_PKG_DIR = _rospack.get_path('baxter_artist')
    """Location of the baxter_artist/ package
    """
else:
    ROS_ENABLED = False
    """Are we running in a ROS environment?
    """

    ARTIST_PKG_DIR = os.path.join(os.path.dirname(__file__),os.pardir,os.pardir)
    print ARTIST_PKG_DIR
    """Location of the baxter_artist/ package
    """

ARTIST_SHARE_DIR = os.path.join(ARTIST_PKG_DIR,'share/')
""" Location of the share/ directory
"""

IMAGE_PATH = os.path.join(ARTIST_SHARE_DIR,'images/')
""" Location of the images/ directory
"""

CONFIG_FILENAME = os.path.join(ARTIST_SHARE_DIR,'conf.json')
""" Location of the conf.json file with neutral position.
"""

KEYS_FILENAME = os.path.join(ARTIST_SHARE_DIR,'keys.json')
""" Location of the keys.json file with the joint positions for each key.
"""

# export BaxterController, Leaner. must stay after rospack lines above!!
from .controller import BaxterController
from .learner import Learner
from .performer import Performer
from .publisher import NotePublisher