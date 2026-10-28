from app import db
from app.models import Usuario


class UsuarioRepository:
    def obtener_todos(self):
        return Usuario.query.all()

    def obtener_por_id(self, usuario_id):
        return db.session.get(Usuario, usuario_id)

    def obtener_por_correo(self, correo):
        return Usuario.query.filter_by(correo=correo).first()

    def guardar(self, usuario):
        db.session.add(usuario)
        db.session.commit()
        return usuario

    def actualizar(self):
        db.session.commit()