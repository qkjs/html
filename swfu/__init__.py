from flask import Flask

app = Flask(__name__)

import swfu.views.index.__init__
import swfu.views.support.__init__
import swfu.views.apiTest.__init__
import swfu.views.fileDown.__init__
import swfu.views.fileDown.__init__
import swfu.views.hrTools.__init__


