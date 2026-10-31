const ZOOM_KEYS = new Set(["+", "=", "-", "_", "0"]);
const GESTURE_EVENTS = ["gesturestart", "gesturechange", "gestureend"];

let installed = false;

function preventGesture(event: Event) {
  event.preventDefault();
}

function preventWheelZoom(event: WheelEvent) {
  if (!event.ctrlKey && !event.metaKey) return;
  event.preventDefault();
}

function preventKeyboardZoom(event: KeyboardEvent) {
  if (!event.ctrlKey && !event.metaKey) return;
  if (!ZOOM_KEYS.has(event.key)) return;
  event.preventDefault();
  event.stopPropagation();
}

export function installZoomLock() {
  if (installed) return;
  installed = true;

  window.addEventListener("wheel", preventWheelZoom, {
    passive: false,
    capture: true,
  });
  window.addEventListener("keydown", preventKeyboardZoom, {
    capture: true,
  });

  for (const eventName of GESTURE_EVENTS) {
    document.addEventListener(eventName, preventGesture, {
      passive: false,
    });
  }
}
