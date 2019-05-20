from npsflaskapp import app

@app.route('/')
@app.route('/index')
def index():
    return "Yeet!"
