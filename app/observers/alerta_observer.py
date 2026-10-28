from abc import ABC, abstractmethod


class ObservadorContrato(ABC):
    @abstractmethod
    def actualizar(self, contrato):
        pass


class AlertaVencimientoObserver(ObservadorContrato):
    def actualizar(self, contrato):
        dias_restantes = contrato.calcular_dias_restantes()

        if 0 <= dias_restantes <= 30:
            return {
                "tipo": "Vencimiento",
                "mensaje": (
                    f"El contrato {contrato.numero_contrato} vence en "
                    f"{dias_restantes} días."
                )
            }

        return None