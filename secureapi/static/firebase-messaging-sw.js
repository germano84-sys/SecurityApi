self.addEventListener("push", function (event) {
  let payload = {};

  try {
    payload = event.data ? event.data.json() : {};
  } catch (_error) {
    payload = {};
  }

  const notification = payload.notification || {};
  const title = notification.title || "SecurityApi";
  const options = {
    body: notification.body || "Notificacion recibida",
    data: payload.data || {},
  };

  event.waitUntil(self.registration.showNotification(title, options));
});
