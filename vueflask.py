from flask import Flask

# We subclass Flask to achive compatibility with Vue.js
class VueFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='{{{',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='}}}',
    ))