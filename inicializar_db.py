from app import create_app, db
from app.models import Rol, Usuario

app = create_app()

with app.app_context():

    # Crear todas las tablas definidas en los modelos
    db.create_all()

    roles_iniciales = [
        {
            "nombre": "Administrador",
            "descripcion": "Gestiona usuarios, roles y supervisa el sistema."
        },
        {
            "nombre": "Funcionario",
            "descripcion": "Registra y actualiza la información contractual."
        },
        {
            "nombre": "Supervisor",
            "descripcion": "Consulta contratos, alertas y seguimiento contractual."
        }
    ]

    for datos_rol in roles_iniciales:
        rol_existente = Rol.query.filter_by(
            nombre=datos_rol["nombre"]
        ).first()

        if not rol_existente:
            nuevo_rol = Rol(
                nombre=datos_rol["nombre"],
                descripcion=datos_rol["descripcion"]
            )
            db.session.add(nuevo_rol)

    db.session.commit()

    rol_admin = Rol.query.filter_by(
        nombre="Administrador"
    ).first()

    admin_existente = Usuario.query.filter_by(
        correo="admin@sigec.local"
    ).first()

    if not admin_existente:
        administrador = Usuario(
            nombre="Administrador SIGEC",
            correo="admin@sigec.local",
            estado=True,
            rol_id=rol_admin.id
        )

        administrador.set_password("Admin123*")

        db.session.add(administrador)
        db.session.commit()

    print("Base de datos SIGEC inicializada correctamente.")