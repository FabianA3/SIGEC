from app import db


class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(30), default="Pendiente", nullable=False)
    observacion = db.Column(db.Text, nullable=True)

    contrato_id = db.Column(
        db.Integer,
        db.ForeignKey("contratos.id"),
        nullable=False
    )

    contrato = db.relationship(
        "Contrato",
        backref=db.backref("pagos", lazy=True)
    )

    def __repr__(self):
        return f"<Pago {self.id} - {self.estado}>"