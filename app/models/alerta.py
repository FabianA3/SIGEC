from app import db


class Alerta(db.Model):
    __tablename__ = "alertas"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_generacion = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        nullable=False
    )
    estado = db.Column(db.String(30), default="Pendiente", nullable=False)

    contrato_id = db.Column(
        db.Integer,
        db.ForeignKey("contratos.id"),
        nullable=False
    )

    contrato = db.relationship(
        "Contrato",
        backref=db.backref("alertas", lazy=True)
    )

    def marcar_como_revisada(self):
        self.estado = "Revisada"

    def __repr__(self):
        return f"<Alerta {self.tipo} - {self.estado}>"