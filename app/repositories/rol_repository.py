from app import db
from app.models import Rol


class RolRepository:
    def obtener_todos(self):
        return Rol.query.all()

    def obtener_por_id(self, rol_id):
        return db.session.get(Rol, rol_id)