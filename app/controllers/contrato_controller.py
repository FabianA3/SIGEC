from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app.decorators import roles_requeridos


contrato_bp = Blueprint(
    "contrato_controller",
    __name__
)

@contrato_bp.route("/contratos", methods=["GET", "POST"])
@login_required
def contratos():
    from datetime import datetime
    from app.models import Contrato
    from app.repositories.contrato_repository import ContratoRepository
    from app.repositories.contratista_repository import ContratistaRepository
    from app.services.alerta_service import AlertaService

    contrato_repository = ContratoRepository()
    contratista_repository = ContratistaRepository()

    if request.method == "POST":
        if current_user.rol.nombre == "Supervisor":
            abort(403)

        numero_contrato = request.form.get("numero_contrato")
        objeto = request.form.get("objeto")
        valor = request.form.get("valor")

        contrato_existente = contrato_repository.obtener_por_numero(
            numero_contrato
        )

        if contrato_existente:
            lista_contratos = contrato_repository.obtener_todos()
            lista_contratistas = contratista_repository.obtener_todos()

            return render_template(
                "contratos.html",
                contratos=lista_contratos,
                contratistas=lista_contratistas,
                error="Ya existe un contrato con este número."
            )

        fecha_inicio = request.form.get("fecha_inicio")
        fecha_terminacion = request.form.get("fecha_terminacion")
        contratista_id = request.form.get("contratista_id")

        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_terminacion = datetime.strptime(
            fecha_terminacion, "%Y-%m-%d"
        ).date()

        if fecha_terminacion < fecha_inicio:
            lista_contratos = contrato_repository.obtener_todos()
            lista_contratistas = contratista_repository.obtener_todos()

            return render_template(
                "contratos.html",
                contratos=lista_contratos,
                contratistas=lista_contratistas,
                error=(
                    "La fecha de terminación no puede ser anterior "
                    "a la fecha de inicio."
                )
            )

        nuevo_contrato = Contrato(
            numero_contrato=numero_contrato,
            objeto=objeto,
            valor=valor,
            fecha_inicio=fecha_inicio,
            fecha_terminacion=fecha_terminacion,
            contratista_id=int(contratista_id)
        )

        contrato_repository.guardar(nuevo_contrato)
        AlertaService().evaluar_contrato(nuevo_contrato)

        return redirect(url_for("contrato_controller.contratos"))

    buscar = request.args.get("buscar", "").strip()
    estado = request.args.get("estado", "").strip()

    lista_contratos = contrato_repository.buscar_y_filtrar(
        buscar,
        estado
    )

    lista_contratistas = contratista_repository.obtener_todos()

    return render_template(
        "contratos.html",
        contratos=lista_contratos,
        contratistas=lista_contratistas,
        buscar=buscar,
        estado=estado
    )

@contrato_bp.route("/contratos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("Administrador", "Funcionario")
def editar_contrato(id):
    from datetime import datetime
    from app.repositories.contrato_repository import ContratoRepository
    from app.repositories.contratista_repository import ContratistaRepository
    from app.services.alerta_service import AlertaService

    contrato_repository = ContratoRepository()
    contratista_repository = ContratistaRepository()
    contrato = contrato_repository.obtener_por_id(id)

    if not contrato:
        return "Contrato no encontrado", 404

    lista_contratistas = contratista_repository.obtener_todos()

    if request.method == "POST":
        numero_contrato = request.form.get("numero_contrato")
        objeto = request.form.get("objeto")
        valor = request.form.get("valor")

        fecha_inicio = datetime.strptime(
            request.form.get("fecha_inicio"), "%Y-%m-%d"
        ).date()

        fecha_terminacion = datetime.strptime(
            request.form.get("fecha_terminacion"), "%Y-%m-%d"
        ).date()

        estado = request.form.get("estado")
        contratista_id = request.form.get("contratista_id")

        contrato_existente = contrato_repository.obtener_por_numero_excluyendo_id(
            numero_contrato,
            id
        )

        if contrato_existente:
            return render_template(
                "editar_contrato.html",
                contrato=contrato,
                contratistas=lista_contratistas,
                error="Ya existe otro contrato con este número."
            )

        if fecha_terminacion < fecha_inicio:
            return render_template(
                "editar_contrato.html",
                contrato=contrato,
                contratistas=lista_contratistas,
                error=(
                    "La fecha de terminación no puede ser anterior "
                    "a la fecha de inicio."
                )
            )

        contrato.numero_contrato = numero_contrato
        contrato.objeto = objeto
        contrato.valor = valor
        contrato.fecha_inicio = fecha_inicio
        contrato.fecha_terminacion = fecha_terminacion
        contrato.estado = estado
        contrato.contratista_id = int(contratista_id)

        contrato_repository.actualizar()
        AlertaService().evaluar_contrato(contrato)

        return redirect(url_for("contrato_controller.contratos"))

    return render_template(
        "editar_contrato.html",
        contrato=contrato,
        contratistas=lista_contratistas
    )