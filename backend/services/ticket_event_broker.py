import json
from queue import Empty, Queue
from threading import Lock


class TicketEventBroker:
    def __init__(self):
        self.listeners = []
        self.lock = Lock()

    def subscribe(self):
        listener = Queue()

        with self.lock:
            self.listeners.append(listener)

        return listener

    def unsubscribe(self, listener):
        with self.lock:
            if listener in self.listeners:
                self.listeners.remove(listener)

    def publish(self, event_name, payload):
        event = {
            "event": event_name,
            "data": payload,
        }

        with self.lock:
            listeners = list(self.listeners)

        for listener in listeners:
            listener.put(event)

    def stream(self, listener, user):
        try:
            yield self.format_event("connected", {"message": "Conectado a acciones en tiempo real"})

            while True:
                try:
                    event = listener.get(timeout=20)
                    if self.should_deliver(event, user):
                        yield self.format_event(event["event"], event["data"])
                except Empty:
                    yield ": keep-alive\n\n"
        finally:
            self.unsubscribe(listener)

    def should_deliver(self, event, user):
        visibility = event["data"].get("visibility", "all")

        if visibility == "all":
            return True

        if visibility == "admins":
            return user.get("rol") == "admin"

        if visibility == "ticket":
            ticket = event["data"].get("ticket") or {}
            return user.get("rol") == "admin" or ticket.get("usuario_id") == user.get("id")

        if visibility == "user":
            event_user = event["data"].get("user") or {}
            return user.get("rol") == "admin" or event_user.get("id") == user.get("id")

        return False

    def format_event(self, event_name, payload):
        return f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"


ticket_event_broker = TicketEventBroker()
