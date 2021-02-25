from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import psycopg2

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://dbimpacta:impacta#2020@dbimpacta.postgresql.dbaas.com.br/dbimpacta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:741741@localhost/teste'
app.debug = True
db = SQLAlchemy(app)
app.secret_key = "oi"
app.permanent_session_lifetime = timedelta(minutes=15)


class Peca(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Float)
    description = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    date_ins = db.Column(db.DateTime)
    date_edt = db.Column(db.DateTime)

    def __init__(self, price, description, quantity, date_ins, date_edt):
        self.price = price
        self.description = description
        self.quantity = quantity
        self.date_ins = date_ins
        self.date_edt = date_edt

    def __repr__(self):
        return '<Peça %r>' % self.description


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(50))
    name = db.Column(db.String(80))
    cpf = db.Column(db.String(14))
    date_ins = db.Column(db.DateTime)

    def __init__(self, email, password, name, cpf, date_ins):
        self.email = email
        self.password = password
        self.date_ins = date_ins
        self.name = name
        self.cpf = cpf


@app.route('/', methods=['POST', 'GET'])
def index():
    classeFlash = 'alert alert-success'
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user is None:
            flash('Incorrect email or password.')
            classeFlash = 'alert alert-danger'
        else:
            session.permanent = True
            session['user'] = user.name
            return redirect(url_for('stock'))
    if 'user' in session:
        return redirect(url_for('stock'))
    return render_template('index.html', classeFlash=classeFlash)


@app.route('/adduser', methods=['POST', 'GET'])
def adduser():
    if request.method == 'POST':
        newuser = User(
            request.form['email'], request.form['password'], request.form['name'], request.form['cpf'], request.form['date_ins'])
        db.session.add(newuser)
        db.session.commit()
        flash('User created.')
        return redirect(url_for('index'))
    return render_template('addUser.html')


@app.route('/stock')
def stock():
    if "user" in session:
        allPecas = Peca.query.all()
        return render_template('estoque.html', pecas=allPecas)
    else:
        return redirect(url_for('index'))


@app.route('/stock/filter/<filter>', methods=['POST', 'GET'])
def filter(filter):
    if "user" in session:
        if filter == 'word':
            word = request.form['search']
            search = "%{}%".format(word)
            allPecas = Peca.query.filter(Peca.description.like(search)).all()
            # print(Peca.query.filter(Peca.description.like(search)))
        elif filter == 'quantity':
            allPecas = Peca.query.order_by(Peca.quantity).all()
            # print(Peca.query.order_by(Peca.quantity.desc()))
        return render_template('estoque.html', pecas=allPecas)
    else:
        return redirect(url_for('index'))


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        peca = Peca(request.form['price'], request.form['description'], request.form['quantity'],
                    request.form['date_ins'], None)
        db.session.add(peca)
        db.session.commit()
        return redirect(url_for('stock'))
    return render_template('addPeça.html')


@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    firstPeca = Peca.query.filter_by(id=id).first()
    if request.method == 'POST':
        firstPeca.price = request.form['price']
        firstPeca.description = request.form['description']
        firstPeca.quantity = request.form['quantity']
        firstPeca.date_edt = request.form['date_edt']
        db.session.commit()
        return redirect(url_for('stock'))
    return render_template('editPeça.html', pecas=firstPeca)


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    selectedPeca = Peca.query.filter_by(id=id).first()
    db.session.delete(selectedPeca)
    db.session.commit()
    return 'deleted'


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have logged out')
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
