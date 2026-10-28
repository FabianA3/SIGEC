from app import db


class Contratista(db.Model):
    __tablename__ = "contratistas"

    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(20), nullable=False)
    numero_documento = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )
    nombre_razon_social = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return f"<Contratista {self.nombre_razon_social}>"