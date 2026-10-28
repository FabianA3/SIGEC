from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.decorators import roles_requeridos


usuario_bp = Blueprint(
    "usuario_controller",
    __name__
)


@usuario_bp.route("/usuarios", methods=["GET", "POST"])
@login_required
@roles_requeridos("Administrador")
def usuarios():
    from app.models import Usuario
    from app.repositories.usuario_repository import UsuarioRepository
    from app.repositories.rol_repository import RolRepository

    usuario_repository = UsuarioRepository()
    rol_repository = RolRepository()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        rol_id = request.form.get("rol_id")

        if not nombre or not correo or not password or not rol_id:
            return render_template(
                "usuarios.html",
                usuarios=usuario_repository.obtener_todos(),
                roles=rol_repository.obtener_todos(),
                error="Todos los campos son obligatorios."
            )

        if usuario_repository.obtener_por_correo(correo):
            return render_template(
                "usuarios.html",
                usuarios=usuario_repository.obtener_todos(),
                roles=rol_repository.obtener_todos(),
                error="Ya existe un usuario con este correo."
            )

        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            rol_id=int(rol_id),
            estado=True
        )
        nuevo_usuario.set_password(password)
        usuario_repository.guardar(nuevo_usuario)

        return redirect(url_for("usuario_controller.usuarios"))

    return render_template(
        "usuarios.html",
        usuarios=usuario_repository.obtener_todos(),
        roles=rol_repository.obtener_todos()
    )

@usuario_bp.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
@login_required
@roles_requeridos("Administrador")
def editar_usuario(id):
    from app.repositories.usuario_repository import UsuarioRepository
    from app.repositories.rol_repository import RolRepository

    usuario_repository = UsuarioRepository()
    rol_repository = RolRepository()

    usuario = usuario_repository.obtener_por_id(id)

    if not usuario:
        return "Usuario no encontrado", 404

    roles = rol_repository.obtener_todos()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        rol_id = request.form.get("rol_id")
        estado = request.form.get("estado") == "1"

        if not nombre or not correo or not rol_id:
            return render_template(
                "editar_usuario.html",
                usuario=usuario,
                roles=roles,
                error="Nombre, correo y rol son obligatorios."
            )

        usuario_existente = usuario_repository.obtener_por_correo(correo)

        if usuario_existente and usuario_existente.id != id:
            return render_template(
                "editar_usuario.html",
                usuario=usuario,
                roles=roles,
                error="Ya existe otro usuario con este correo."
            )

        usuario.nombre = nombre
        usuario.correo = correo
        usuario.rol_id = int(rol_id)
        usuario.estado = estado

        usuario_repository.actualizar()

        return redirect(url_for("usuario_controller.usuarios"))

    return render_template(
        "editar_usuario.html",
        usuario=usuario,
        roles=roles
    )