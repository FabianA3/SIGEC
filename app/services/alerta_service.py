from app import db
from app.models import Alerta
from app.observers.alerta_observer import AlertaVencimientoObserver


class AlertaService:
    def __init__(self):
        self.observadores = [AlertaVencimientoObserver()]

    def evaluar_contrato(self, contrato):
        alertas_generadas = []

        for observador in self.observadores:
            resultado = observador.actualizar(contrato)

            if resultado:
                alerta_existente = Alerta.query.filter_by(
                    contrato_id=contrato.id,
                    tipo=resultado["tipo"]
                ).first()

            if alerta_existente:
                alerta_existente.mensaje = resultado["mensaje"]
            else:
                nueva_alerta = Alerta(
                    tipo=resultado["tipo"],
                    mensaje=resultado["mensaje"],
                    contrato_id=contrato.id
                )

                db.session.add(nueva_alerta)
                alertas_generadas.append(nueva_alerta)

        db.session.commit()
        return alertas_generadas