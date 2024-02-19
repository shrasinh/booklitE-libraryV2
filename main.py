from application.setup import app
from controllers.Admin import *
from controllers.User import *
from controllers.Generic import *
from controllers.Api import *


if __name__ == '__main__':
    app.run(debug=True,port=5500)