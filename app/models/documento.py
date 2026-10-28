from app import db


class Documento(db.Model):
    __tablename__ = "documentos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        nullable=False
    )

    contrato_id = db.Column(
        db.Integer,
        db.ForeignKey("contratos.id"),
        nullable=False
    )

    contrato = db.relationship(
        "Contrato",
        backref=db.backref("documentos", lazy=True)
    )

    def __repr__(self):
        return f"<Documento {self.nombre}>"