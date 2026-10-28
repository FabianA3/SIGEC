from functools import wraps
from flask import abort
from flask_login import current_user


def roles_requeridos(*roles_permitidos):
    def decorador(funcion):
        @wraps(funcion)
        def funcion_protegida(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if current_user.rol.nombre not in roles_permitidos:
                abort(403)

            return funcion(*args, **kwargs)

        return funcion_protegida

    return decorador