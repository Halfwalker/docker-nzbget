#!/usr/bin/env python
#
##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Move download directory to a new destination.
#
# NZBGet unpacks a download not in the intermediate directory but in an
# _unpack directory inside the destination directory. This can cause issues
# when the destination directory is monitored by an outside application
# like Plex that opens files and prevents them from being moved after
# unpacking is finished.
#
# This script allows a download directory to be moved during post-processing
# after the download has been unpacked to prevent interference from outside
# applications during unpacking.
#
# NOTE: This script requires Python to be installed on your system.
##############################################################################
### OPTIONS                                                                ###

# Set the directory where you want the download to be moved to.
#DestinationDirectory=

# If set to yes, the category will be appended to the DestinationDirectory (yes, no).
#AppendCategories=yes

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################
import os
import sys
import shutil

# NZBGet Exit Codes
NZBGET_POSTPROCESS_SUCCESS = 93
NZBGET_POSTPROCESS_ERROR = 94
NZBGET_POSTPROCESS_NONE = 95

if not os.environ.has_key('NZBOP_SCRIPTDIR'):
    print "This script can only be called from NZBGet (11.0 or later)."
    sys.exit(0)

if os.environ['NZBOP_VERSION'][0:5] < '11.0':
    print "[ERROR] NZBGet Version %s is not supported. Please update NZBGet." % (str(os.environ['NZBOP_VERSION']))
    sys.exit(0)

# We want to make sure the download has finished properly before moving it to a new location.
status = 0
if os.environ.has_key('NZBPP_TOTALSTATUS'):
    if not os.environ['NZBPP_TOTALSTATUS'] == 'SUCCESS':
        print "[ERROR] Download failed with status %s." % (os.environ['NZBPP_STATUS'])
        status = 1

else:
    # Check par status
    if os.environ['NZBPP_PARSTATUS'] == '1' or os.environ['NZBPP_PARSTATUS'] == '4':
        print "[ERROR] Par-repair failed."
        status = 1

    # Check unpack status
    if os.environ['NZBPP_UNPACKSTATUS'] == '1':
        print "[ERROR] Unpack failed."
        status = 1

    if os.environ['NZBPP_UNPACKSTATUS'] == '0' and os.environ['NZBPP_PARSTATUS'] == '0':
        # Unpack was skipped due to nzb-file properties or due to errors during par-check

        if os.environ['NZBPP_HEALTH'] < 1000:
            print "[ERROR] Download health is compromised and Par-check/repair disabled or no .par2 files found."
            status = 1
        else:
            print "[WARNING] Download health is compromised and Par-check/repair disabled or no .par2 files found."

destination = os.environ['NZBPO_DESTINATIONDIRECTORY']

if os.environ['NZBPO_APPENDCATEGORIES'] == 'yes':
    destination = os.path.join(destination, os.environ['NZBPP_CATEGORY'])

# Resolve any symlinks in the path so we can compare them later.
# Note that this has no effect on Windows as of yet (see https://bugs.python.org/issue9949).
destinationReal = os.path.realpath(destination)
directoryReal = os.path.realpath(os.environ['NZBPP_DIRECTORY'])

# Make sure both the source and destination exist and are directories or the move may have some unexpected results.
if not os.path.isdir(directoryReal):
    print "[ERROR] Current destination directory \"%s\" does not exist." % (os.environ['NZBPP_DIRECTORY'])
    status = 1

if not os.path.isdir(destinationReal):
    print "[ERROR] New destination directory \"%s\" does not exist." % (destination)
    status = 1

if status == 1:
    sys.exit(NZBGET_POSTPROCESS_ERROR)

# No need to move on reprocessing if the download is already in the proper destination directory.
if destinationReal == os.path.dirname(directoryReal):
    print "[INFO] Skipping move, download directory \"%s\" is already in the proper destination." % (os.environ['NZBPP_DIRECTORY'])
    sys.exit(NZBGET_POSTPROCESS_NONE)

print "[INFO] Moving download directory"
print "[DETAIL] - Source: %s" % (directoryReal)
print "[DETAIL] - Destination: %s" % (destinationReal)

try:
    shutil.move(directoryReal, destinationReal)
except:
    print "[ERROR] Failed to move download directory"
    sys.exit(NZBGET_POSTPROCESS_ERROR)

# This line is picked up by NZBGet and updates the destination directory to its new location so that
# any other post-processing scripts that run after this script will also receive the new location.
print "[NZB] DIRECTORY=%s" % (os.path.join(destination, os.path.basename(os.environ['NZBPP_DIRECTORY'])))

sys.exit(NZBGET_POSTPROCESS_SUCCESS)