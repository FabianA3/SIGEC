from app import db


class NovedadContractual(db.Model):
    __tablename__ = "novedades_contractuales"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

    contrato_id = db.Column(
        db.Integer,
        db.ForeignKey("contratos.id"),
        nullable=False
    )

    contrato = db.relationship(
        "Contrato",
        backref=db.backref("novedades", lazy=True)
    )

    def __repr__(self):
        return f"<NovedadContractual {self.tipo}>"