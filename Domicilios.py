from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.exceptions import HTTPException
import pymysql.cursors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass

#tratamiento de errores









#descifrar la contraseña
DESPLAZAMIENTO = 3
alfanumericos = 'abcdefghijklmnñopqrstuvwxyz0123456789 ' 

#recibe un mensaje y lo devuelve cifrado con cifrado cesar
def cifrar(mensaje):
    #si el mensaje posee almenos un caracter a cifrar...
    if (len(mensaje) > 0):  
        #se pasan el mensaje a encriptar a minusculas
        formatoMensaje = mensaje.lower()
        mensajeCifrado = ""#almacena el mensaje cifrado
        for caracter in formatoMensaje:
            #se calcula el indice con el cual se accedera al caracter de la cadena alfanumericos
            #con el cual se formara el mensaje cifrado 
            indiceEnAlfanumerico = alfanumericos.find(caracter) + DESPLAZAMIENTO
            #si el indice obtenido excede el rango de la cadena...
            if indiceEnAlfanumerico > 37:
                indiceEnAlfanumerico = indiceEnAlfanumerico - 38
            #se concatena el caracter cifrado para componer el mensaje
            mensajeCifrado = mensajeCifrado + alfanumericos[indiceEnAlfanumerico]
        return mensajeCifrado

#decifrar contraseña 
def decifrar(mensaje):
    #si el mensaje posee almenos un caracter a descifrar...
    if (len(mensaje) > 0):
        #se pasan el mensaje a desencriptar a minusculas
        formatoMensaje = mensaje.lower()
        mensajeDecifrado = ""#almacena el mensaje descifrado
        for caracter in formatoMensaje:
            #se calcula el indice con el cual se accedera al caracter de la cadena alfanumericos
            #con el cual se formara el mensaje descifrado 
            indiceEnAlfanumerico = alfanumericos.find(caracter) - DESPLAZAMIENTO
            #si el indice obtenido excede el rango de la cadena...
            if indiceEnAlfanumerico < 0:
                indiceEnAlfanumerico = 38 - indiceEnAlfanumerico
            #se concatena el caracter descifrado para componer el mensaje
            mensajeDecifrado = mensajeDecifrado + alfanumericos[indiceEnAlfanumerico]
        return mensajeDecifrado


app = Flask(__name__)
app.secret_key = "sk"

#index
@app.route('/')
def index():
    #sesion del usuario
    if 'usuario' in session:   
        usuario = session['usuario']
        return render_template('index.html', nombres=usuario)
    return render_template('index.html')
"""
#t""ratamiento de errores
@app.errorhandler(Exception)
def globalErrores(error):
  if isinstance(error, pymysql.err.IntegrityError):
    return render_template('error.html', mensajeError="El usuario ya existe")
  mensajeError = "Lo sentimos a ocurrido un error"
  return render_template('error.html',mensajeError = mensajeError)  

#MANEJADOR DE EL ERROR 404   
@app.errorhandler(404)
def errorNoExiste(error):
    mensajeError = "Lo sentimos. El sitio solicitado no existe."
    return render_template('error.html', mensajeError=mensajeError), 404
"""
#index del administrador
@app.route('/indexAdministrador')
def indexAdministrador():
  if 'usuario' in session:   
      usuario = session['usuario']
      return render_template('indexAdministrador.html',nombres=usuario)
  return render_template('index.html')

#index del empleado
@app.route('/indexEmpleado')
def indexEmpleado():
  if 'usuario' in session:   
      usuario = session['usuario']
      return render_template('indexEmpleado.html',nombres=usuario)
  return render_template('index.html')

#registro del usuario o empleado
@app.route('/registro/',methods = ['GET','POST'])
def registro():
  if request.method == 'POST':
    NumeroDocumento= request.form['numeroDocumento']
    Nombres = request.form['nombres']
    Apellidos = request.form['apellidos']
    Email = request.form['email']
    Contraseña = request.form['password']
    Telefono = request.form['telefono']
    Direccion = request.form['direccion']
    #conexion a la base de datos
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (numeroDocumento,nombres,apellidos,email,contraseña,telefono,direccion) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
    NumeroDocumento,Nombres,Apellidos,Email,cifrar(Contraseña),Telefono,Direccion))
    conn.commit()
    conn.close()
    flash(Nombres + ' su registro fue exitoso')
    return redirect(url_for('login'))
  
  return render_template('registro.html')

#login de usuarios
@app.route('/login/',methods = ['GET','POST'])
def login():
  if request.method == 'POST':
    #se recuperan datos del formulario
    usuario = request.form['email']
    password = request.form['password']
    #conexion a la base de datos
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd ="", db="Entregapp" )
    cursor = conn.cursor()
    cursor.execute("SELECT contraseña,email,role FROM usuarios WHERE email=%s", (usuario))
    resultado = cursor.fetchone()
    conn.close()
    
    #si el usuario no existe..
    if resultado is None:
      flash('El usuario no esta registrado!! Por favor registrese')
      return  redirect(url_for('login'))
         
    #si el password coincide con el del usuario...
    if password == decifrar(resultado[0]):
      #se crea la sesion del usuario
      session['usuario'] = usuario
          
      #si el correo corresponde es el  administrador
      if resultado[1]=="maurobetarios@gmail.com":
        flash('Bienvenido Administrador a domicilios Entregapp')
        return render_template('indexAdministrador.html',nombres = usuario)
          
      #si el correo corresponde a un empleado                      
      if resultado[2]=="empleado":
        flash('Bienvenido empleado')
        return render_template('IndexEmpleado.html', nombres = usuario)

      #si el correo corresponde a un usurio    
      flash('Bienvenido ' + usuario + ', a Domicilios Entregapp')
      return render_template('indexUsuario.html',nombres = usuario)  

      #si la contraseña es incorrecta  
    else:
      flash('usuario o contraseña incorrecta')
      return redirect(url_for('login'))

  return render_template('login.html')

#agregar empleados desde la vista del administrador
@app.route('/registroEmpleados/',methods = ['GET','POST'])
def registroEmpleados():
  if request.method == 'POST':
    NumeroDocumento= request.form['numeroDocumento']
    Nombres = request.form['nombres']
    Apellidos = request.form['apellidos']
    Email = request.form['email']
    Contraseña = request.form['password']
    Telefono = request.form['telefono']
    Direccion = request.form['direccion']
    Role = request.form['role']
    #conexion a la base de datos
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (numeroDocumento,nombres,apellidos,email,contraseña,telefono,direccion,role) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (
    NumeroDocumento,Nombres,Apellidos,Email,cifrar(Contraseña),Telefono,Direccion,Role))
    conn.commit()
    conn.close()
    flash(' El registro del empleado fue exitoso')
    return redirect(url_for('indexAdministrador'))  
  return render_template('registroEmpleados.html')

  #usuarios existentes enl aplicacion desde la vista del administrador
@app.route('/informacionUsuarios')
def informacionUsuarios():
  if 'usuario' in session:   
    usuario = session['usuario']
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    resultado =cursor.fetchall()
    conn.close()
  return render_template('informacionUsuarios.html',usuarios = resultado, nombres = usuario)

#eliminar usuarios desde la vista del administrador
@app.route('/eliminar/<usuarios>', methods=['GET'])
def eliminar(usuarios):
    if 'usuario' in session:
        usuario = session["usuario"]
        borrarCliente = usuarios
        #conexion a la base de datos
        conn = pymysql.connect(
        host="localhost", port=3306, user="root",
        passwd="", db="Entregapp")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE numeroDocumento=%s", (borrarCliente))
        conn.commit()
        conn.close()
        flash('Usted acaba de eliminar al cliente con identificacion ' + borrarCliente )  
        return redirect(url_for('informacionUsuarios'))

 #paquetes existentes enl aplicacion desde la vista del administrador
@app.route('/paquetes')
def paquetes():
  if 'usuario' in session:   
    usuario = session['usuario']
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paquetes")
    resultado =cursor.fetchall()
    conn.close()
  return render_template('paquetes.html', paquetes = resultado, nombres = usuario)

#actualizar informacion empleado
@app.route('/updateEmpleado/<numeroDocumento>',methods = ['GET','POST'])
def updateEmpleado(numeroDocumento):
  if 'usuario' in session:
    usuario = session["usuario"]

    #consulta a base datos del numero de documento del ususario
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("SELECT numeroDocumento FROM usuarios WHERE email = %s", (usuario))
    resultado =cursor.fetchone()
    conn.close
    
    #formulario de actualizar informacion de empleados
    if request.method == 'POST':
      NumeroDocumento = request.form['numeroDocumento']
      Nombres = request.form['nombres']
      Apellidos = request.form['apellidos']
      Email = request.form['email']
      Contraseña = request.form['password']
      Telefono = request.form['telefono']
      Direccion = request.form['direccion']
      #conexion a la base de datos    
      conn = pymysql.connect(
      host="localhost", port=3306, user="root",
      passwd="", db="Entregapp")
      cursor = conn.cursor()
      cursor.execute("""UPDATE usuarios SET numeroDocumento = %s,nombres = %s, apellidos = %s,email = %s,contraseña = %s,
      telefono = %s,direccion = %s WHERE email=%s""",
      (NumeroDocumento,Nombres,Apellidos,Email,cifrar(Contraseña),Telefono,Direccion,usuario))
      conn.commit()
      conn.close
      flash('se actualizo correctamente')
      return redirect(url_for('login'))
    return render_template('actualizarEmpleado.html')

#eliminar cuenta de empleado
@app.route('/borrar', methods=['GET'])
def borrar():
  if 'usuario' in session:
    usuario = session["usuario"]
    #consulta a base datos del numero de documento del ususario
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("SELECT numeroDocumento FROM usuarios WHERE email = %s", (usuario))
    resultado =cursor.fetchone()
    conn.close
    if 'usuario' in session:
      usuario = session["usuario"]
    #conexion a la base de datos
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE email=%s", (usuario))
    conn.commit()
    conn.close()
    flash('Usted acaba de eliminar al cliente con identificacion '  )  
    return redirect(url_for('login'))

#envio de correo del contacto del index
@app.route('/contacto',methods = ['POST'])
def contacto():
    if request.method == 'POST':
      Nombre= request.form['nombre']
      Correo = request.form['correo']    
      Telefono = request.form['telefono']
      Mensaje = request.form['mensaje']
      cliente = 'smtp.gmail.com: 587'#si el cliente es google  
      remitente = 'EnviosEntregapp@gmail.com'#cuenta correo q envia    
      correoDestinatario = 'EnviosEntregapp@gmail.com'
      asunto = "mensaje contacto"
      mensaje =   Correo  +  ' ' +  Mensaje
      servidor = smtplib.SMTP(cliente)
      servidor.starttls()
      servidor.ehlo()
      servidor.login(remitente, "entregapp12345")
      mess = mensaje
      msg = MIMEMultipart()
      msg.attach(MIMEText(mess, 'plain'))
      msg['From'] = remitente
      msg['To'] = correoDestinatario
      msg['Subject'] = asunto
      servidor.sendmail(msg['From'], msg['To'], msg.as_string())
      servidor.quit()      
      return render_template('index.html')

#paquetes usuario
@app.route('/paquetes/',methods = ['GET','POST'])
def paquetescliente():
  if 'usuario' in session:
    usuario = session["usuario"]
    #conexion a base de datos
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp" )
    cursor = conn.cursor()
    cursor.execute("SELECT numeroDocumento FROM usuarios WHERE email=%s", (usuario))
    DocumentoUsuario = cursor.fetchone()
    conn.close() 
         
    if request.method == 'POST':
      Peso = request.form['pesoPaquete']
      DireccionRecoger = request.form['direccionRecoger']    
      Telefono = request.form['telefono']
      DireccionEntrega = request.form['direccionEntrega']
      Descripcion = request.form['descripcionPaquete']
      #conexion a base de datos
      conn = pymysql.connect(
      host="localhost", port=3306, user="root",
      passwd="", db="Entregapp")
      cursor = conn.cursor()
      cursor.execute("INSERT INTO Paquetes (peso,direccionrecoger,telefono,direccionEntrega,descripcion,usuarioPedido)VALUES (%s,%s,%s,%s,%s,%s)",
      (Peso,DireccionRecoger,Telefono,DireccionEntrega,Descripcion,DocumentoUsuario))
      conn.commit()
      conn.close()
      #envio de correos
      cliente = 'smtp.gmail.com: 587'#si el cliente es google
      remitente = 'enviosentregapp@gmail.com'#cuenta correo que envia el correo
      password = 'entregapp12345'
      correoDestinatario = usuario
      asunto = "Pedido de paquetes de domicilios entregapp"
      mensaje = "Gracias por tenernos en cuenta"
      servidor = smtplib.SMTP(cliente)
      servidor.starttls()
      servidor.ehlo()
      servidor.login(remitente, password)
      mess = mensaje
      msg = MIMEMultipart()
      msg.attach(MIMEText(mess, 'plain'))
      msg['From'] = remitente
      msg['To'] = correoDestinatario
      msg['Subject'] = asunto
      servidor.sendmail(msg['From'] , msg['To'], msg.as_string())
      servidor.quit()
    return render_template('pagos.html')
  return redirect('paquetescliente.html')
"""
#Comidas usuario
@app.route('/paquetes/',methods = ['GET','POST'])
def paquetescliente():
  if 'usuario' in session:
    usuario = session["usuario"]
    #conexion a base de datos
    conn = pymysql.connect(
    host="localhost", port=3306, user="root",
    passwd="", db="Entregapp" )
    cursor = conn.cursor()
    cursor.execute("SELECT numeroDocumento FROM usuarios WHERE email=%s", (usuario))
    DocumentoUsuario = cursor.fetchone()
    conn.close() 
         
    if request.method == 'POST':
      Peso = request.form['pesoPaquete']
      DireccionRecoger = request.form['direccionRecoger']    
      Telefono = request.form['telefono']
      DireccionEntrega = request.form['direccionEntrega']
      Descripcion = request.form['descripcionPaquete']
      #conexion a base de datos
      conn = pymysql.connect(
      host="localhost", port=3306, user="root",
      passwd="", db="Entregapp")
      cursor = conn.cursor()
      cursor.execute("INSERT INTO Paquetes (peso,direccionrecoger,telefono,direccionEntrega,descripcion,usuarioPedido)VALUES (%s,%s,%s,%s,%s,%s)",
      (Peso,DireccionRecoger,Telefono,DireccionEntrega,Descripcion,DocumentoUsuario))
      conn.commit()
      conn.close()
      #envio de correos
      cliente = 'smtp.gmail.com: 587'#si el cliente es google
      remitente = 'enviosentregapp@gmail.com'#cuenta correo que envia el correo
      password = 'entregapp12345'
      correoDestinatario = usuario
      asunto = "Pedido de paquetes de domicilios entregapp"
      mensaje = "Gracias por tenernos en cuenta"
      servidor = smtplib.SMTP(cliente)
      servidor.starttls()
      servidor.ehlo()
      servidor.login(remitente, password)
      mess = mensaje
      msg = MIMEMultipart()
      msg.attach(MIMEText(mess, 'plain'))
      msg['From'] = remitente
      msg['To'] = correoDestinatario
      msg['Subject'] = asunto
      servidor.sendmail(msg['From'] , msg['To'], msg.as_string())
      servidor.quit()
    return render_template('pagos.html')
  return redirect('paquetescliente.html')
"""
@app.route('/comidas/',methods = ['GET','POST'])
def comidas():
  if request.method == 'POST':
      Peso = request.form['peso']
      Tipo = request.form['tipo']    
      Precio = request.form['precio']
      conn = pymysql.connect(
      host="localhost", port=3306, user="root",
      passwd="", db="Entregapp")
      cursor = conn.cursor()
      cursor.execute("INSERT INTO comidas (peso,tipo,precio)VALUES (%s,%s,%s)",
      (Peso,Tipo,Precio))
      conn.commit()
      conn.close()
  return render_template('comidas.html')

#cerrar sesion
@app.route('/logout', methods=['GET'])
def cerrarSesion():
    if 'usuario' in session:
        session.pop('usuario',None)
        flash(' usted finalizo sesion')
    return redirect(url_for('index'))

if __name__ == '__main__':
   app.run(debug = True)
