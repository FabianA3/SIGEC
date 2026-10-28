from app import db
from app.models import Contrato, Contratista


class ContratoRepository:
    def obtener_todos(self):
        return Contrato.query.all()

    def obtener_por_id(self, contrato_id):
        return db.session.get(Contrato, contrato_id)

    def obtener_por_numero(self, numero_contrato):
        return Contrato.query.filter_by(
            numero_contrato=numero_contrato
        ).first()

    def obtener_por_numero_excluyendo_id(self, numero_contrato, contrato_id):
        return Contrato.query.filter(
            Contrato.numero_contrato == numero_contrato,
            Contrato.id != contrato_id
        ).first()

    def buscar_y_filtrar(self, buscar="", estado=""):
        consulta = Contrato.query.join(Contratista)

        if buscar:
            patron = f"%{buscar}%"
            consulta = consulta.filter(
                db.or_(
                    Contrato.numero_contrato.ilike(patron),
                    Contrato.objeto.ilike(patron),
                    Contratista.nombre_razon_social.ilike(patron)
                )
            )

        if estado:
            consulta = consulta.filter(Contrato.estado == estado)

        return consulta.all()

    def guardar(self, contrato):
        db.session.add(contrato)
        db.session.commit()
        return contrato

    def actualizar(self):
        db.session.commit()