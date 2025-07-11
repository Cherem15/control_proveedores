from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
from datetime import datetime
import pdfkit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///control_proveedores.db'
db = SQLAlchemy(app)

# MODELOS
class Proveedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(100))
    contacto = db.Column(db.String(100))
    rfc = db.Column(db.String(50))

class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cliente = db.Column(db.String(100))
    ubicacion = db.Column(db.String(100))
    presupuesto = db.Column(db.Float, default=0)

class Concepto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(200), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    unidad = db.Column(db.String(50))
    precio_unitario = db.Column(db.Float, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'))

    proveedor = db.relationship('Proveedor')
    proyecto = db.relationship('Proyecto')

# RUTAS PRINCIPALES
@app.route('/')
def index():
    return redirect(url_for('lista_proyectos'))

@app.route('/proveedores', methods=['GET', 'POST'])
def proveedores():
    if request.method == 'POST':
        nuevo = Proveedor(
            nombre=request.form['nombre'],
            empresa=request.form['empresa'],
            contacto=request.form['contacto'],
            rfc=request.form['rfc']
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('proveedores'))
    todos = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=todos)

@app.route('/proyectos', methods=['GET', 'POST'])
def lista_proyectos():
    if request.method == 'POST':
        nuevo = Proyecto(
            nombre=request.form['nombre'],
            cliente=request.form['cliente'],
            ubicacion=request.form['ubicacion'],
            presupuesto=request.form['presupuesto']
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('lista_proyectos'))
    proyectos = Proyecto.query.all()
    return render_template('proyectos.html', proyectos=proyectos)

@app.route('/proyectos/<int:proyecto_id>/conceptos', methods=['GET', 'POST'])
def conceptos(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    proveedores = Proveedor.query.all()
    if request.method == 'POST':
        nuevo = Concepto(
            descripcion=request.form['descripcion'],
            cantidad=request.form['cantidad'],
            unidad=request.form['unidad'],
            precio_unitario=request.form['precio_unitario'],
            proveedor_id=request.form['proveedor_id'],
            proyecto_id=proyecto_id
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('conceptos', proyecto_id=proyecto_id))
    conceptos = Concepto.query.filter_by(proyecto_id=proyecto_id).all()
    return render_template('conceptos.html', proyecto=proyecto, conceptos=conceptos, proveedores=proveedores)

@app.route('/cotizacion/<int:proyecto_id>')
def cotizacion(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    conceptos = Concepto.query.filter_by(proyecto_id=proyecto_id).all()
    return render_template('cotizacion.html', proyecto=proyecto, conceptos=conceptos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
