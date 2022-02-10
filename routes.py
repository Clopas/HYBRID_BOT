from flask import Flask, render_template, request
from forms import SignupForm
import credentials
import main
import asyncio

app = Flask(__name__)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/learningflask'
# db.init_app(app)

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


# app.secret_key = "development-key"

# @app.route("/")
# def index():
#   return render_template("index.html")
#
# @app.route("/about")
# def about():
#   return render_template("about.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if request.method == "POST":
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            print(form.account_id_3commas.data, form.api_key_3commas.data, form.api_secret_3commas.data,
                  form.api_key_ftx.data, form.api_secret_ftx.data)
            # asyncio.set_event_loop(asyncio.SelectorEventLoop())
            credentials.api_key_3commas = form.api_key_3commas.data
            credentials.api_secret_3commas = form.api_secret_3commas.data
            credentials.api_key_ftx = form.api_key_ftx.data
            credentials.api_secret_ftx = form.api_secret_ftx.data
            get_or_create_eventloop().run_until_complete(main.main())

            return 'DCA-GRID bot start!'


    elif request.method == "GET":
        return render_template('signup.html', form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
