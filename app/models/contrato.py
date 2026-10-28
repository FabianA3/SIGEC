from datetime import date
from app import db


class Contrato(db.Model):
    __tablename__ = "contratos"

    id = db.Column(db.Integer, primary_key=True)
    numero_contrato = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )
    objeto = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_terminacion = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(30), default="Activo", nullable=False)

    contratista_id = db.Column(
        db.Integer,
        db.ForeignKey("contratistas.id"),
        nullable=False
    )

    contratista = db.relationship(
        "Contratista",
        backref=db.backref("contratos", lazy=True)
    )

    def calcular_dias_restantes(self):
        return (self.fecha_terminacion - date.today()).days

    def __repr__(self):
        return f"<Contrato {self.numero_contrato}>"