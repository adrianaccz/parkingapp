from flask import Flask, redirect, url_for, render_template, request, session
from datetime import datetime
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb as mysql
import pymysql
from markupsafe import escape
import MySQLdb.cursors
import re


app = Flask(__name__)


app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'parkingapp'
app.config['MYSQL_PORT'] = 8889



mysql = MySQL(app)

# Crear ruta url
@app.route('/')
def index():
    return render_template('index.html')    # Redirige la pagina al html

@app.route('/quienesSomos')
def quienesSomos():
    return render_template('quienesSomos.html')

@app.route('/soyAdministrador')
def soyAdministrador():
    return render_template('soyAdmin.html')

@app.route('/soyDueño')
def soyDueño():
    return render_template('soyDueño.html')

@app.route('/soyVisitante')
def soyVisitante():
    return render_template('soyVisitante.html')   

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    error=None

    if request.method == 'POST':

        nombre= request.form['nombre']
        apellidos= request.form['apellidos']
        email= request.form['email']
        cuentanos= request.form['cuentanos']

        if email is '':
            return render_template('contacto.html', error="Ingrese el email")
        elif cuentanos is '':
            return render_template('contacto.html', error="Ingrese datos en Cuentanos")
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO contacto VALUES(NULL, %s, %s, %s, %s)", (nombre, apellidos, email, cuentanos))
            cur.connection.commit()
            return render_template('mensaje_enviado.html')
    
    return render_template('contacto.html')

@app.route('/ingresar', methods=['GET', 'POST'])
def ingresar():
    error=''
    if request.method == 'POST':
        email=False
        password=False

        email= request.form['email']
        password= request.form['password']

        if email is '':
            return render_template('ingresar.html', error="Ingrese su Email")

        if password is '':
            return render_template('ingresar.html', error="Ingrese su Contraseña")

        if email and password:
            cur = mysql.connection.cursor()
            prueba = cur.execute("SELECT * FROM usuarios WHERE email =%s AND password=%s", (email, password))
            resultado = cur.fetchall()
            cur.connection.commit()
            
            if prueba == 0:
                return render_template('ingresar.html', error='Contraseña o correo incorrecto')
            else:
                session['email'] = request.form['email']
                session['password'] = request.form['password']
                session['id_usuarios'] = resultado[0][0]
                session['nombre'] = resultado[0][1]
                session['apellidos'] = resultado[0][2]
                session['telefono'] = resultado[0][5]

                return redirect(url_for('mi_perfil'))
    return render_template('ingresar.html', error=error)

        

@app.route('/resetear_passw')
def rest_passw():
    return render_template('resetear_passw.html')

@app.route('/registrarte', methods=['GET', 'POST'])
def registrate():
    error=None
    if request.method == 'POST':
        correo = False
        contra = False

        nombre= request.form['nombre']
        apellidos= request.form['apellidos']
        email= request.form['email']
        perfil=request.form['perfil']
        telefono=request.form['telefono']
        password= request.form['password']

        if nombre is '':
            return render_template('registrar.html',error="Ingrese su nombre")

        if apellidos is '':
            return render_template('registrar.html',error="Ingrese sus apellidos")

        if re.match ('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',email.lower()):
            correo =  True
        else:
            return render_template('registrar.html',error="Correo incorrecto")

        if 8 <= len(password) <=16:
            if re.search('[a-z]', password) and re.search('[A-Z]', password):
                if re.search('[0-9]', password):
                    if re.search('[$@#]', password):
                        contra = True
        else:
            return render_template('registrar.html',error="password incorrecto")  
        
        if perfil == '1' and '2' and '3':
            perfil = True
        else:
            return render_template('registrar.html',error="Seleccione un perfil")

        if contra and correo:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO usuarios VALUES(NULL, %s, %s, %s, %s, %s, %s)", (nombre, apellidos, email, perfil, telefono, password))
            cur.connection.commit()
            return render_template('registro_exitoso.html')
        

    return render_template('registrar.html')

@app.route('/asigna_esta', methods=['GET', 'POST'])
def asignar_esta():
    mensaje=None
    resultados=None
    resultados2=None

    if 'email' in session:

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios")
        resultados = cur.fetchall()
        cur.connection.commit()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM estacionamientos")
        resultados2 = cur.fetchall()
        cur.connection.commit()

        if request.method == 'POST':

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO esta_usuarios VALUES(NULL, %s, %s)", (str(request.form['usuarios']), str(request.form['estacionamientos'])))
            cur.connection.commit()

            return render_template('asigna_esta.html', mensaje="Registro Exitoso!!", resultados=resultados, resultados2=resultados2)

        return render_template('asigna_esta.html', resultados=resultados, resultados2=resultados2)
    else:
        return render_template('index.html')

@app.route('/mi_perfil', methods=['GET', 'POST'])
def mi_perfil():
    mensaje = None
    if 'email' in session:

        if request.method == 'POST':
            correo = False
            contra = False

            nombre= request.form['nombre']
            apellidos= request.form['apellidos']
            email= request.form['email']
            perfil=request.form['perfil']
            telefono=request.form['telefono']
            password= request.form['password']

            if nombre is '':
                return render_template('registrar.html',error="Ingrese su nombre")

            if apellidos is '':
                return render_template('registrar.html',error="Ingrese sus apellidos")

            if re.match ('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',email.lower()):
                correo =  True
            else:
                return render_template('registrar.html',error="Correo incorrecto")

            if 8 <= len(password) <=16:
                if re.search('[a-z]', password) and re.search('[A-Z]', password):
                    if re.search('[0-9]', password):
                        if re.search('[$@#]', password):
                            contra = True
            else:
                return render_template('registrar.html',error="password incorrecto")  
            
            if perfil == '1' and '2' and '3':
                perfil = True
            else:
                return render_template('registrar.html',error="Seleccione un perfil")

            if contra and correo:
                
                id_usuarios = session['id_usuarios'] 
                cur = mysql.connection.cursor()
                cur.execute("update usuarios  set nombre =%s, apellidos=%s, email=%s, password=%s, telefono=%s, perfil=%s WHERE id_usuarios=%s",(nombre, apellidos, email, password, telefono, perfil, id_usuarios))
                cur.connection.commit()

                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM usuarios WHERE id_usuarios =%s",(str(session['id_usuarios'])))
                resultado = cur.fetchall()
                cur.connection.commit()

                return render_template('mi_perfil.html',resultado=resultado[0], mensaje="Has actualizado tus datos con exito!!")
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE id_usuarios =%s",(str(session['id_usuarios'])))
            resultado = cur.fetchall()
            cur.connection.commit()
        return render_template('mi_perfil.html',resultado=resultado[0])

    else:
        return redirect(url_for('ingresar'))

@app.route('/adm_esta', methods=['GET', 'POST'])
def adm_esta():
    error= None
    mensaje = None
    if 'email' in session:
        if 'num_estacionamiento':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM estacionamientos")
            resultado_estacionamiento = cur.fetchall()
            cur.connection.commit()
            #return render_template('adm_esta.html', resultado_estacionamiento=resultado_estacionamiento)

        if request.method == 'POST':

            num_estacionamiento = request.form['num_estacionamiento']
            piso_estacionamiento = request.form['piso_estacionamiento']
            tipo_estacionamiento = request.form['tipo_estacionamiento']
            
            if num_estacionamiento == '':
                return render_template('adm_esta.html', error="Error: Ingrese número de estacionamiento")
            elif piso_estacionamiento == '':
                return render_template('adm_esta.html', error="Error: Ingrese piso de estacionamiento")
            elif tipo_estacionamiento == '-1':
                return render_template('adm_esta.html', error="Error: Ingrese tipo de estacionamiento")
            else:
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO estacionamientos VALUES(NULL, %s, %s, %s)", (num_estacionamiento, piso_estacionamiento, tipo_estacionamiento))
                cur.connection.commit()
                return render_template('adm_esta.html', mensaje="Estacionamiento ingresado con exito!!", resultado_estacionamiento=resultado_estacionamiento)

        return render_template('adm_esta.html', resultado_estacionamiento=resultado_estacionamiento)
    else:
        return redirect(url_for('index'))


@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.pop('email', None)
    session.pop('password', None)
    session.pop('id_usuarios', None)
    session.pop('telefono', None)

    return redirect(url_for('index'))

# Para colocar hora en la pagina
@app.context_processor
def date():
    return {
        'now': datetime.utcnow()
    }

#Crear app
# Esto es para saber si efectivamente hay una app creada y abrirla

if __name__ == '__main__': 
    app.run(host='127.0.0.1',port=4455,debug=True)
