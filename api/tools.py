from flask import render_template

def render(template, args):
    return render_template(template, **args)
