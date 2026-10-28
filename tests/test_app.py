from app import create_app, db
from app.models import Rol, Usuario, Contratista, Contrato
from app.repositories.contrato_repository import ContratoRepository
from app.observers.alerta_observer import AlertaVencimientoObserver
from datetime import date


def test_crear_aplicacion():
    app = create_app()

    assert app is not None
    assert app.name == "app"


def test_inicio_requiere_autenticacion():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as cliente:
        respuesta = cliente.get("/")

        assert respuesta.status_code == 302
        assert "/login" in respuesta.headers["Location"]


def test_cola_agrega_y_procesa_tarea():
    from app.queues.task_queue import TaskQueue

    cola = TaskQueue()

    assert cola.cantidad_pendientes() == 0

    cola.agregar_tarea({"tipo": "generar_reporte", "formato": "csv"})
    assert cola.cantidad_pendientes() == 1

    resultado = cola.procesar_siguiente()

    assert resultado["estado"] == "procesada"
    assert resultado["tarea"]["tipo"] == "generar_reporte"
    assert cola.cantidad_pendientes() == 0


def test_login_con_credenciales_validas():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        rol = Rol(nombre="Administrador", descripcion="Rol de prueba")
        db.session.add(rol)
        db.session.commit()

        usuario = Usuario(
            nombre="Usuario Prueba",
            correo="prueba@sigec.local",
            estado=True,
            rol_id=rol.id
        )
        usuario.set_password("Prueba123*")
        db.session.add(usuario)
        db.session.commit()

        with app.test_client() as cliente:
            respuesta = cliente.post(
                "/login",
                data={
                    "correo": "prueba@sigec.local",
                    "password": "Prueba123*"
                },
                follow_redirects=False
            )

            assert respuesta.status_code == 302
            assert respuesta.headers["Location"].endswith("/")

        db.session.remove()
        db.drop_all()


def test_login_rechaza_password_incorrecta():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        rol = Rol(nombre="Administrador", descripcion="Rol de prueba")
        db.session.add(rol)
        db.session.commit()

        usuario = Usuario(
            nombre="Usuario Prueba",
            correo="prueba@sigec.local",
            estado=True,
            rol_id=rol.id
        )
        usuario.set_password("Prueba123*")
        db.session.add(usuario)
        db.session.commit()

        with app.test_client() as cliente:
            respuesta = cliente.post(
                "/login",
                data={
                    "correo": "prueba@sigec.local",
                    "password": "PasswordIncorrecta"
                },
                follow_redirects=False
            )

            assert respuesta.status_code == 200
            assert "Correo o contraseña incorrectos." in respuesta.get_data(as_text=True)

        db.session.remove()
        db.drop_all()



def test_supervisor_no_puede_acceder_a_usuarios():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        rol = Rol(nombre="Supervisor", descripcion="Rol de prueba")
        db.session.add(rol)
        db.session.commit()

        usuario = Usuario(
            nombre="Supervisor Prueba",
            correo="supervisor.prueba@sigec.local",
            estado=True,
            rol_id=rol.id
        )
        usuario.set_password("Supervisor123*")
        db.session.add(usuario)
        db.session.commit()

        with app.test_client() as cliente:
            cliente.post(
                "/login",
                data={
                    "correo": "supervisor.prueba@sigec.local",
                    "password": "Supervisor123*"
                }
            )

            respuesta = cliente.get("/usuarios")

            assert respuesta.status_code == 403

        db.session.remove()
        db.drop_all()



def test_repositorio_obtiene_contrato_por_numero():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()

        contratista = Contratista(
            tipo_documento="CC",
            numero_documento="1234567890",
            nombre_razon_social="Contratista Repository",
            correo="repository@sigec.local",
            telefono="3001234567"
        )
        db.session.add(contratista)
        db.session.commit()

        contrato = Contrato(
            numero_contrato="TEST-001-2026",
            objeto="Contrato para probar el patrón Repository",
            valor=1000000,
            fecha_inicio=date(2026, 10, 27),
            fecha_terminacion=date(2026, 11, 27),
            estado="Activo",
            contratista_id=contratista.id
        )

        repositorio = ContratoRepository()
        repositorio.guardar(contrato)

        encontrado = repositorio.obtener_por_numero("TEST-001-2026")

        assert encontrado is not None
        assert encontrado.numero_contrato == "TEST-001-2026"
        assert encontrado.contratista_id == contratista.id

        db.session.remove()
        db.drop_all()



def test_observer_genera_alerta_para_contrato_proximo_a_vencer():
    contrato = Contrato(
        numero_contrato="OBS-001-2026",
        objeto="Contrato para probar el patrón Observer",
        valor=1000000,
        fecha_inicio=date.today(),
        fecha_terminacion=date.today(),
        estado="Activo",
        contratista_id=1
    )

    observer = AlertaVencimientoObserver()
    resultado = observer.actualizar(contrato)

    assert resultado is not None
    assert resultado["tipo"] == "Vencimiento"