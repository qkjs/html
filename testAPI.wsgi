import sys
#Expand Python classes path with your app's path
sys.path.insert(0, "/var/www/testAPI")

from testAPI import app
application = app
