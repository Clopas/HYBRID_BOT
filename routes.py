import importlib
# import os
# import sys
from flask import Flask, render_template, request
from forms import SignupForm
import credentials
import functions
from functions import close_all, cleanup, run, position
from celery_flask import make_celery
import asyncio

# sys.path.append(os.getcwd())

flask_app = Flask(__name__)

flask_app.config.update(
    CELERY_BROKER_URL='amqp://localhost//',
    CELERY_RESULT_BACKEND='rpc://localhost//',

)

celery = make_celery(flask_app)


# ##################### Celery Tasks ##############################
@celery.task(name='routes.celery_close_all')
def celery_close_all(b, c):
    # import functions
    # importlib.reload(functions)
    functions.api_key_3commas = b
    functions.api_secret_3commas = c
    return close_all()


@celery.task(name='routes.celery_cleanup')
def celery_cleanup(b, c):
    functions.api_key_3commas = b
    functions.api_secret_3commas = c
    return cleanup()


@celery.task(name='routes.celery_run')
def celery_run(a, b, c, d, e):
    functions.account_id_3commas = a
    functions.api_key_3commas = b
    functions.api_secret_3commas = c
    functions.api_key_ftx = d
    functions.api_secret_ftx = e
    return run()


# def get_or_create_eventloop():
#    try:
#        return asyncio.get_event_loop()
#    except RuntimeError as ex:
#        if "There is no current event loop in thread" in str(ex):
#            loop = asyncio.new_event_loop()
#            asyncio.set_event_loop(loop)
#            return asyncio.get_event_loop()

flask_app.secret_key = 'b5943ed7668424f03997a729a4d7a08adc53e59983dd6710d84bc1e4c0ac75d4'


@flask_app.route("/", methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if request.method == "POST":
        if not form.validate_on_submit():
            return render_template('signup.html', form=form)

        else:
            # asyncio.set_event_loop(asyncio.SelectorEventLoop())
            credentials.account_id_3commas = form.account_id_3commas_signup.data
            credentials.api_key_3commas = form.api_key_3commas_signup.data
            credentials.api_secret_3commas = form.api_secret_3commas_signup.data
            credentials.api_key_ftx = form.api_key_ftx_signup.data
            credentials.api_secret_ftx = form.api_secret_ftx_signup.data

            # from functions import close_all, cleanup, main
            import functions
            importlib.reload(functions)

            if form.run_button.data:
                celery_run.delay(form.account_id_3commas_signup.data, form.api_key_3commas_signup.data,
                                 form.api_secret_3commas_signup.data, form.api_key_ftx_signup.data,
                                 form.api_secret_ftx_signup.data)
                # get_or_create_eventloop().run_until_complete(main())
                return render_template("result-run.html")

            elif form.close_all_button.data:
                celery_close_all.delay(form.api_key_3commas_signup.data,
                                       form.api_secret_3commas_signup.data)
                # result_close_all.get()
                # get_or_create_eventloop().run_until_complete(close_all())
                # close_all()
                return render_template("result-closeall.html")

            elif form.cleanup_button.data:
                celery_cleanup.delay(form.api_key_3commas_signup.data,
                                     form.api_secret_3commas_signup.data)
                # result_cleanup.get()
                # get_or_create_eventloop().run_until_complete(cleanup())
                return render_template("result-cleanup.html")
            elif form.position_button.data:
                return position()

    elif request.method == "GET":
        return render_template('signup.html', form=form)


if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', debug=True)
