# vim:fileencoding=utf-8:ts=4:sw=4:sts=4:expandtab

from flask import Flask, redirect, request
import Granite
from Granite import QA, HS, JN, ML
import random

Redis = Granite.OpenRedis(Host = 'redis', Database = 0)
app = Flask(__name__)

@app.route("/deletename/", methods = ['POST', 'GET'])
def delete():

    name = request.args.get('name')
    Redis.lrem('dinner_name_list', name, 0)

    UI = Layout()
    UI('''
        <h2>Confirm Delete</h2>
        <p>Are you sure you want to delete {name}?</p>
        <form method="post" action=''' + QA(request.url) + '''>
            <button class="btn btn-primary" type="submit">Delete ''' + HS(name) + '''</button>
            or
            <a class="btn btn-primary" href="/">Cancel</a>
        </form>
    ''')

    return UI.Render()

@app.route("/")
def index():

    names = Redis.lrange_str('dinner_name_list', 0, -1)

    UI = Layout()
    UI('''
        <h2>People List</h2>
        <table>
            
            <tr>
                <th>Names</th>
                <th>Action</th>
            </tr>
            ''' +
            
            JN('''
            <tr>
                <td>''' + HS(name) + '''</td>
                <td><a class="btn btn-primary" href=''' + QA(ML('/deletename/', name=name)) + '''>Delete</a></td>
            </tr>
            ''' for name in names) +
            
            '''
        </table>
    ''')

    return UI.Render()

@app.route("/dinner")
def dinner():

    names = Redis.lrange_str('dinner_name_list', 0, -1)

    UI = Layout()
    UI('''
        <h2>Who's paying?</h2>
        <p>''' + HS(random.choice(names)) +''' is paying for the dinner.</p>
        <a class="btn btn-primary" href="/">Cancel</a>
    ''')

    return UI.Render()

@app.route("/add", methods=['POST', 'GET'])
def add():

    errors = []
    name = ""

    for _ in (range(1) if request.method == 'POST' else range(0)):
        name = request.form['name'].strip()

        if not name:
            errors.append('Name is required.')
        if len(name) > 10:
            errors.append('Name must not be longer than 10 characters.')

        if errors:
            break

        Redis.lpush_str('dinner_name_list', name)

        return redirect('/')

    UI = Layout()
    UI('''
        <h2>Add Person</h2>
        ''' + JN('''
            <div>''' + HS(e) + '''</div>
        ''' for e in errors) + '''
        <form method="post" action=''' + QA(request.url) + '''>
            <input class="form-control" type="text" id="name" name="name" value=''' + QA(name) + '''><br>
            <button class="btn btn-primary" type="submit">Save</button>
             or <a class="btn btn-primary" href="/">Cancel</a>
        </form>

        <hr>


    ''')

    return UI.Render()

class Layout():
    def __init__(self):
        self.Container = True
        self.Body = []

    def __call__(self, content):
        self.Body.append(str(content))

    def Render(self):
        return ('''
            <!doctype html>
            <html lang="en">
            <head>
                <!-- Required meta tags -->
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">

                <!-- Bootstrap CSS -->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
                <link href="/static/app.css" rel="stylesheet"  crossorigin="anonymous">

                <title>Dinner Payor</title>
            </head>
            <body>
                ''' + ('''
                <div class="container">
                    <nav>
                        <a class="btn btn-primary" href="/">Home</a>
                        <a class="btn btn-primary" href="/add">Add Person</a>
                        <a class="btn btn-primary" href="/dinner">Who's Paying?</a>
                    </nav>
                    <hr>
                    ''' + ''.join(self.Body) + '''
                </div>
                ''' if self.Container else '''
                    ''' + ''.join(self.Body) + '''
                ''') + '''

                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
            </body>
            </html>
            ''')

''' questions
couldn't for _ in (range(1) if request.method == 'POST' else range(0)): be replaced by some sort of try-except model?
do we have a Granite Cog?
why do I have to break and restart Flask when I edit app.py (but not other files)?
'''
