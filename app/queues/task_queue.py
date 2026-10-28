from queue import Queue


class TaskQueue:
    def __init__(self):
        self._queue = Queue()

    def agregar_tarea(self, tarea):
        self._queue.put(tarea)

    def obtener_tarea(self):
        if self._queue.empty():
            return None
        return self._queue.get()

    def cantidad_pendientes(self):
        return self._queue.qsize()

    def procesar_siguiente(self):
        tarea = self.obtener_tarea()

        if tarea is None:
            return None

        return {
            "estado": "procesada",
            "tarea": tarea
        }

# Instancia compartida de la cola para el prototipo SIGEC
task_queue = TaskQueue()