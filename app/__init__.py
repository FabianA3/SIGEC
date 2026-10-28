from flask import Flask, app, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from app.decorators import roles_requeridos
from app.queues.task_queue import task_queue
import os
from dotenv import load_dotenv

load_dotenv()



# Extensiones de la aplicación
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(configuracion_pruebas=None):
    app = Flask(__name__)

    # Configuración básica
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "sigec-clave-desarrollo")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sigec.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")

    if configuracion_pruebas:
        app.config.update(configuracion_pruebas)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # Registrar modelos
    from app import models

    # Registrar controladores (Blueprints)
    from app.controllers.contrato_controller import contrato_bp
    from app.controllers.usuario_controller import usuario_bp

    app.register_blueprint(contrato_bp)
    app.register_blueprint(usuario_bp)

    # Configuración de autenticación
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return db.session.get(Usuario, int(user_id))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            from app.models import Usuario

            correo = request.form.get("correo")
            password = request.form.get("password")

            usuario = Usuario.query.filter_by(correo=correo).first()

            if usuario and usuario.estado and usuario.check_password(password):
                login_user(usuario)
                return redirect(url_for("inicio"))

            return render_template(
                "login.html",
                error="Correo o contraseña incorrectos."
            )

        return render_template("login.html")

    @app.route("/")
    @login_required
    def inicio():
        from app.models import (
            Contratista,
            Contrato,
            Alerta,
            Pago,
            Documento,
            NovedadContractual
        )

        total_contratistas = Contratista.query.count()
        total_contratos = Contrato.query.count()
        contratos_activos = Contrato.query.filter_by(estado="Activo").count()
        alertas_pendientes = Alerta.query.filter_by(estado="Pendiente").count()
        total_pagos = Pago.query.count()
        total_documentos = Documento.query.count()
        total_novedades = NovedadContractual.query.count()

        return render_template(
            "dashboard.html",
            total_contratistas=total_contratistas,
            total_contratos=total_contratos,
            contratos_activos=contratos_activos,
            alertas_pendientes=alertas_pendientes,
            total_pagos=total_pagos,
            total_documentos=total_documentos,
            total_novedades=total_novedades
        )

    @app.route("/contratistas", methods=["GET", "POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def contratistas():
        from app.models import Contratista

        if request.method == "POST":
            tipo_documento = request.form.get("tipo_documento")
            numero_documento = request.form.get("numero_documento")
            nombre_razon_social = request.form.get("nombre_razon_social")
            correo = request.form.get("correo")
            telefono = request.form.get("telefono")
            if not tipo_documento or not numero_documento or not nombre_razon_social:
                lista_contratistas = Contratista.query.all()

                return render_template(
                    "contratistas.html",
                    contratistas=lista_contratistas,
                    error="Tipo de documento, número de documento y nombre son obligatorios."
                )  
            contratista_existente = Contratista.query.filter_by(
                numero_documento=numero_documento
            ).first()

            if contratista_existente:
                lista_contratistas = Contratista.query.all()

                return render_template(
                    "contratistas.html",
                    contratistas=lista_contratistas,
                    error="Ya existe un contratista con este número de documento."
                )                     
            nuevo_contratista = Contratista(
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                nombre_razon_social=nombre_razon_social,
                correo=correo,
                telefono=telefono
            )

            db.session.add(nuevo_contratista)
            db.session.commit()

            return redirect(url_for("contratistas"))
        
        lista_contratistas = Contratista.query.all()

        return render_template(
            "contratistas.html",
            contratistas=lista_contratistas
        )

    @app.route("/contratistas/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def editar_contratista(id):
        from app.models import Contratista

        contratista = db.session.get(Contratista, id)

        if not contratista:
            return "Contratista no encontrado", 404

        if request.method == "POST":
            tipo_documento = request.form.get("tipo_documento")
            numero_documento = request.form.get("numero_documento")
            nombre_razon_social = request.form.get("nombre_razon_social")
            correo = request.form.get("correo")
            telefono = request.form.get("telefono")

            contratista_existente = Contratista.query.filter(
                Contratista.numero_documento == numero_documento,
                Contratista.id != id
            ).first()

            if contratista_existente:
                return render_template(
                    "editar_contratista.html",
                    contratista=contratista,
                    error="Ya existe otro contratista con este número de documento."
                )

            contratista.tipo_documento = tipo_documento
            contratista.numero_documento = numero_documento
            contratista.nombre_razon_social = nombre_razon_social
            contratista.correo = correo
            contratista.telefono = telefono

            db.session.commit()

            return redirect(url_for("contratistas"))

        return render_template(
            "editar_contratista.html",
            contratista=contratista
        )

    @app.route("/contratistas/<int:id>/eliminar", methods=["POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def eliminar_contratista(id):
        from app.models import Contratista

        contratista = db.session.get(Contratista, id)

        if not contratista:
            return "Contratista no encontrado", 404

        if contratista.contratos:
            lista_contratistas = Contratista.query.all()

            return render_template(
                "contratistas.html",
                contratistas=lista_contratistas,
                error="No se puede eliminar el contratista porque tiene contratos asociados."
            )

        db.session.delete(contratista)
        db.session.commit()

        return redirect(url_for("contratistas"))


    @app.route("/documentos", methods=["GET", "POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def documentos():
        from app.models import Documento, Contrato

        if request.method == "POST":
            contrato_id = request.form.get("contrato_id")
            nombre = request.form.get("nombre")
            tipo = request.form.get("tipo")
            archivo = request.files.get("archivo")

            if not archivo or archivo.filename == "":
                lista_documentos = Documento.query.order_by(
                    Documento.fecha_registro.desc()
                ).all()
                lista_contratos = Contrato.query.all()

                return render_template(
                    "documentos.html",
                    documentos=lista_documentos,
                    contratos=lista_contratos,
                    error="Debe seleccionar un archivo PDF."
                )

            nombre_seguro = secure_filename(archivo.filename)
            ruta_fisica = os.path.join(
                app.config["UPLOAD_FOLDER"],
                nombre_seguro
            )

            archivo.save(ruta_fisica)
            ruta_archivo = f"uploads/{nombre_seguro}"

            contrato = db.session.get(Contrato, int(contrato_id))

            if not contrato:
                return "Contrato no encontrado", 404

            nuevo_documento = Documento(
                nombre=nombre,
                tipo=tipo,
                ruta_archivo=ruta_archivo,
                contrato_id=contrato.id
            )

            db.session.add(nuevo_documento)
            db.session.commit()

            return redirect(url_for("documentos"))

        lista_documentos = Documento.query.order_by(
            Documento.fecha_registro.desc()
        ).all()

        lista_contratos = Contrato.query.all()

        return render_template(
            "documentos.html",
            documentos=lista_documentos,
            contratos=lista_contratos
        )

    @app.route("/novedades", methods=["GET", "POST"])
    @login_required
    def novedades():
        from datetime import datetime
        from app.models import NovedadContractual, Contrato

        if request.method == "POST":
            if current_user.rol.nombre == "Supervisor":
                return "No tiene permisos para registrar novedades.", 403
            
            contrato_id = request.form.get("contrato_id")
            tipo = request.form.get("tipo")
            fecha = request.form.get("fecha")
            descripcion = request.form.get("descripcion")

            contrato = db.session.get(Contrato, int(contrato_id))

            if not contrato:
                return "Contrato no encontrado", 404

            nueva_novedad = NovedadContractual(
                tipo=tipo,
                fecha=datetime.strptime(fecha, "%Y-%m-%d").date(),
                descripcion=descripcion,
                contrato_id=contrato.id
            )

            db.session.add(nueva_novedad)
            db.session.commit()

            return redirect(url_for("novedades"))

        lista_novedades = NovedadContractual.query.order_by(
            NovedadContractual.fecha.desc()
        ).all()

        lista_contratos = Contrato.query.all()

        return render_template(
            "novedades.html",
            novedades=lista_novedades,
            contratos=lista_contratos
        )


    @app.route("/pagos", methods=["GET", "POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def pagos():
        from datetime import datetime
        from app.models import Pago, Contrato

        if request.method == "POST":
            contrato_id = request.form.get("contrato_id")
            valor = request.form.get("valor")
            fecha_pago = request.form.get("fecha_pago")
            estado = request.form.get("estado")
            observacion = request.form.get("observacion")

            contrato = db.session.get(Contrato, int(contrato_id))

            if not contrato:
                return "Contrato no encontrado", 404

            valor_pago = float(valor)

            total_pagado = sum(
                float(pago.valor)
                for pago in contrato.pagos
                if pago.estado == "Pagado"
            )

            if estado == "Pagado" and total_pagado + valor_pago > float(contrato.valor):
                lista_pagos = Pago.query.order_by(Pago.fecha_pago.desc()).all()
                lista_contratos = Contrato.query.all()
                return render_template(
                    "pagos.html",
                    pagos=lista_pagos,
                    contratos=lista_contratos,
                    error="El total de pagos no puede superar el valor del contrato."
                )

            nuevo_pago = Pago(
                valor=valor,
                fecha_pago=datetime.strptime(fecha_pago, "%Y-%m-%d").date(),
                estado=estado,
                observacion=observacion,
                contrato_id=contrato.id
            )

            db.session.add(nuevo_pago)
            db.session.commit()

            return redirect(url_for("pagos"))

        lista_pagos = Pago.query.order_by(Pago.fecha_pago.desc()).all()
        lista_contratos = Contrato.query.all()

        return render_template(
            "pagos.html",
            pagos=lista_pagos,
            contratos=lista_contratos
        )

    @app.route("/alertas")
    @login_required
    def alertas():
        from app.models import Alerta

        lista_alertas = Alerta.query.order_by(
            Alerta.fecha_generacion.desc()
        ).all()

        return render_template(
            "alertas.html",
            alertas=lista_alertas
        )

    @app.route("/alertas/<int:id>/revisar", methods=["POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def revisar_alerta(id):
        from app.models import Alerta

        alerta = db.session.get(Alerta, id)

        if not alerta:
            return "Alerta no encontrada", 404

        alerta.marcar_como_revisada()
        db.session.commit()

        return redirect(url_for("alertas"))

    @app.route("/reportes")
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def reportes():
        from decimal import Decimal
        from app.models import Contrato

        lista_contratos = Contrato.query.all()
        total_contratos = Contrato.query.count()
        contratos_activos = Contrato.query.filter_by(estado="Activo").count()

        valor_total = sum(
            (contrato.valor for contrato in lista_contratos),
            Decimal("0.00")
        )

        tareas_pendientes = task_queue.cantidad_pendientes()

        return render_template(
            "reportes.html",
            contratos=lista_contratos,
            total_contratos=total_contratos,
            contratos_activos=contratos_activos,
            valor_total=valor_total,
            tareas_pendientes=tareas_pendientes
        )

    @app.route("/reportes/encolar", methods=["POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def encolar_reporte():
        tarea = {
            "tipo": "generar_reporte",
            "formato": "csv",
            "solicitado_por": current_user.correo
        }

        task_queue.agregar_tarea(tarea)

        return redirect(url_for("reportes"))

    @app.route("/reportes/procesar", methods=["POST"])
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def procesar_reporte():
        task_queue.procesar_siguiente()
        return redirect(url_for("reportes"))


    @app.route("/reportes/exportar/csv")
    @login_required
    @roles_requeridos("Administrador", "Funcionario")
    def exportar_reporte_csv():
        import csv
        import io
        from flask import Response
        from app.models import Contrato

        salida = io.StringIO()
        salida.write("\ufeff")
        escritor = csv.writer(salida, delimiter=";")

        escritor.writerow([
            "Número",
            "Contratista",
            "Objeto",
            "Valor",
            "Fecha de inicio",
            "Fecha de terminación",
            "Estado"
        ])

        for contrato in Contrato.query.all():
            escritor.writerow([
                contrato.numero_contrato,
                contrato.contratista.nombre_razon_social,
                contrato.objeto,
                contrato.valor,
                contrato.fecha_inicio,
                contrato.fecha_terminacion,
                contrato.estado
            ])

        return Response(
            salida.getvalue(),
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    "attachment; filename=reporte_contratos_SIGEC.csv"
            }
        )

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    return app