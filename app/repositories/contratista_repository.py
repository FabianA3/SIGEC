from app.models import Contratista


class ContratistaRepository:
    def obtener_todos(self):
        return Contratista.query.all()