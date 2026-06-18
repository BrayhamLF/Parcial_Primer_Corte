import tkinter as tk
import threading
import time

# ╔══════════════════════════════════════════════════════╗
# ║         SIMULADOR DE TRÁFICO INTELIGENTE             ║
# ║    Con hilos, semáforos y vehículos con emojis       ║
# ╚══════════════════════════════════════════════════════╝

# ── PALETA DE COLORES ──────────────────────────────────
HIERBA          = "#1b3626"   # Verde bosque
CARRETERA       = "#263545"   # Gris azulado
LINEA_VIAL      = "#dde6ed"   # Blanco suave
SEMAFORO_CAJA   = "#0a1520"   # Negro azulado
COLOR_TITULO    = "#e8f4f8"
COLOR_SUBTITULO = "#7fb3c8"
PANEL_BG        = "#0c1a28"
INFO_VERDE      = "#00b87a"
INFO_ROJO       = "#e03c3c"
INFO_AMARILLO   = "#e8960f"
INFO_AZUL       = "#3a8ecf"
SEPARADOR       = "#1a3550"

# ── EMOJIS POR DIRECCIÓN ───────────────────────────────
EMOJIS_ESTE  = ["🚗", "🚛", "🚕", "🚗"]
EMOJIS_OESTE = ["🚕", "🚗", "🚛", "🚗"]
EMOJIS_SUR   = ["🚗", "🚕", "🚛", "🚗"]
EMOJIS_NORTE = ["🚕", "🚗", "🚛", "🚗"]

# ── COLOR ESTÁNDAR POR TIPO DE VEHÍCULO ──────────────
COLORES_VEH = {
    "🚗": "#2e86de",   # Azul
    "🚛": "#e07b39",   # Naranja
    "🚕": "#d4ac0d",   # Amarillo
}
FONT_EMOJI_VEH = ("Segoe UI Emoji", 16)

# ── COORDENADAS DEL ESCENARIO ────────────────────────
RD_H_Y1, RD_H_Y2 = 260, 430     # Carretera horizontal
RD_V_X1, RD_V_X2 = 510, 702     # Carretera vertical
CTR_H = (RD_H_Y1 + RD_H_Y2) // 2
CTR_V = (RD_V_X1 + RD_V_X2) // 2

# Carriles de tráfico
CARRIL_ESTE  = 286    # Lane →
CARRIL_OESTE = 402    # Lane ←
CARRIL_SUR   = 660    # Lane ↓ (derecha del centro)
CARRIL_NORTE = 548    # Lane ↑ (izquierda del centro)

# Límites de reset y movimiento
L_MARGEN = -60
R_MARGEN = 1260
B_MARGEN = 740
STEP     = 3
GAP      = 106

# ══════════════════════════════════════════════════════
# VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════
ventana = tk.Tk()
ventana.title("🚦 Simulador de Tráfico Inteligente")
ventana.geometry("1430x680")
ventana.config(bg=PANEL_BG)
ventana.resizable(False, False)

# ── LAYOUT: SIDEBAR IZQUIERDO + CANVAS ────────────────
sidebar = tk.Frame(ventana, bg=PANEL_BG, width=228)
sidebar.pack(side=tk.LEFT, fill=tk.Y)
sidebar.pack_propagate(False)

canvas = tk.Canvas(
    ventana, width=1202, height=680,
    bg="#1a2a3a", highlightthickness=0
)
canvas.pack(side=tk.LEFT)


# ══════════════════════════════════════════════════════
# CLASES DE CONTROL DE TRÁFICO (OOP)
# ══════════════════════════════════════════════════════

class Semaphore:
    def __init__(self, canvas, x, y, direction_label, flow_dir):
        self.canvas = canvas
        self.flow_dir = flow_dir  # "horizontal" o "vertical"
        self.estado = "rojo"

        # Dibujar caja y luces
        self.canvas.create_rectangle(
            x, y, x + 44, y + 122,
            fill=SEMAFORO_CAJA, outline="#1e3a5f", width=2
        )
        self.luz_roja     = self.canvas.create_oval(x + 7, y + 7,  x + 37, y + 38,  fill="gray")
        self.luz_amarilla = self.canvas.create_oval(x + 7, y + 44, x + 37, y + 75,  fill="gray")
        self.luz_verde    = self.canvas.create_oval(x + 7, y + 83, x + 37, y + 114, fill="gray")

        # Dibujar poste y etiqueta
        if y < 260:  # Superior
            self.canvas.create_line(x + 22, y + 122, x + 22, 260, fill="#3a6080", width=6, capstyle="round")
            self.canvas.create_text(x + 22, y - 10, text=direction_label, fill=COLOR_SUBTITULO,
                                    font=("Segoe UI", 8, "bold"), anchor=tk.CENTER)
        else:  # Inferior
            self.canvas.create_line(x + 22, 430, x + 22, y, fill="#3a6080", width=6, capstyle="round")
            self.canvas.create_text(x + 22, y + 130, text=direction_label, fill=COLOR_SUBTITULO,
                                    font=("Segoe UI", 8, "bold"), anchor=tk.CENTER)

        self.actualizar_luces()

    def set_estado(self, estado):
        self.estado = estado
        self.actualizar_luces()

    def actualizar_luces(self):
        colores = {
            "verde":    ("gray",    "gray",    "#00e676"),
            "amarillo": ("gray",    "#ffd740", "gray"),
            "rojo":     ("#ff1744", "gray",    "gray"),
        }
        cr, ca, cv = colores[self.estado]
        self.canvas.itemconfig(self.luz_roja,     fill=cr)
        self.canvas.itemconfig(self.luz_amarilla, fill=ca)
        self.canvas.itemconfig(self.luz_verde,    fill=cv)


class TrafficLightSystem:
    def __init__(self, ventana, semaforos):
        self.ventana = ventana
        self.semaforos = semaforos
        self.estado_horizontal = "verde"
        self.estado_vertical   = "rojo"
        self._aplicar_estados()

    def _aplicar_estados(self):
        for sem in self.semaforos:
            if sem.flow_dir == "horizontal":
                sem.set_estado(self.estado_horizontal)
            else:
                sem.set_estado(self.estado_vertical)

    def iniciar_ciclo(self):
        self.ciclar()

    def ciclar(self):
        try:
            if self.estado_horizontal == "verde":
                self.estado_horizontal = "amarillo"
                self._aplicar_estados()
                self.ventana.after(2000, self.ciclar)

            elif self.estado_horizontal == "amarillo":
                self.estado_horizontal = "rojo"
                self.estado_vertical   = "verde"
                self._aplicar_estados()
                self.ventana.after(6000, self.ciclar)

            elif self.estado_vertical == "verde":
                self.estado_vertical = "amarillo"
                self._aplicar_estados()
                self.ventana.after(2000, self.ciclar)

            else:
                self.estado_vertical   = "rojo"
                self.estado_horizontal = "verde"
                self._aplicar_estados()
                self.ventana.after(6000, self.ciclar)
        except tk.TclError:
            pass


# ══════════════════════════════════════════════════════
# CLASE VEHÍCULO (HEREDA DE THREADING.THREAD)
# ══════════════════════════════════════════════════════

_vid = [0]
def _next_tag():
    _vid[0] += 1
    return f"veh{_vid[0]}"

class Vehicle(threading.Thread):
    def __init__(self, canvas, x, y, emoji, direction, light_system, vehicles_list):
        super().__init__(daemon=True)
        self.canvas = canvas
        self.x = float(x)
        self.y = float(y)
        self.emoji = emoji
        self.direction = direction  # "ESTE", "OESTE", "SUR", "NORTE"
        self.light_system = light_system
        self.vehicles_list = vehicles_list
        self.tag = _next_tag()

        self.horizontal = direction in ("ESTE", "OESTE")
        self.color = COLORES_VEH.get(emoji, "#607d8b")

        # Configurar dimensiones según tipo de vehículo
        if emoji == "🚛":
            self.hw, self.hh = (34, 13) if self.horizontal else (13, 34)
        else:  # "🚗", "🚕", etc.
            self.hw, self.hh = (28, 13) if self.horizontal else (13, 28)

        # Ajuste vertical para compensar alineación del emoji en canvas
        self.dy = -1 if self.horizontal else -2

        # Crear rect + texto en el canvas compartiendo el mismo tag
        self.canvas.create_rectangle(
            self.x - self.hw, self.y - self.hh, self.x + self.hw, self.y + self.hh,
            fill=self.color, outline="#ffffff", width=1, tags=self.tag
        )
        self.canvas.create_text(
            self.x, self.y + self.dy, text=emoji,
            font=FONT_EMOJI_VEH, tags=self.tag
        )

        # Registrar este vehículo en la lista
        self.vehicles_list.append(self)

    def _colisiona(self):
        """Revisa la distancia centro a centro con vehículos adelante en el mismo flujo."""
        for other in self.vehicles_list:
            if other == self:
                continue
            if other.direction != self.direction:
                continue

            if self.direction == "ESTE":
                if other.x > self.x and (other.x - self.x) < GAP:
                    return True
            elif self.direction == "OESTE":
                if other.x < self.x and (self.x - other.x) < GAP:
                    return True
            elif self.direction == "SUR":
                if other.y > self.y and (other.y - self.y) < GAP:
                    return True
            elif self.direction == "NORTE":
                if other.y < self.y and (self.y - other.y) < GAP:
                    return True
        return False

    def _semaforo_permite(self):
        """Determina si el estado del semáforo y la posición permiten avanzar."""
        if self.direction == "ESTE":
            if self.light_system.estado_horizontal == "verde":
                return True
            return not (460 <= self.x + 16 <= 495)

        elif self.direction == "OESTE":
            if self.light_system.estado_horizontal == "verde":
                return True
            return not (717 <= self.x - 16 <= 752)

        elif self.direction == "SUR":
            if self.light_system.estado_vertical == "verde":
                return True
            return not (214 <= self.y + 16 <= 255)

        elif self.direction == "NORTE":
            if self.light_system.estado_vertical == "verde":
                return True
            return not (444 <= self.y - 16 <= 478)
        return True

    def run(self):
        """Bucle de ejecución del hilo del vehículo."""
        while True:
            try:
                if self._semaforo_permite() and not self._colisiona():
                    dx, dy = 0, 0
                    if self.direction == "ESTE":
                        dx = STEP
                    elif self.direction == "OESTE":
                        dx = -STEP
                    elif self.direction == "SUR":
                        dy = STEP
                    elif self.direction == "NORTE":
                        dy = -STEP

                    self.canvas.move(self.tag, dx, dy)
                    self.x += dx
                    self.y += dy

                # Reubicar al inicio al salir del margen
                reset = False
                target_x, target_y = self.x, self.y

                if self.direction == "ESTE" and self.x > R_MARGEN:
                    target_x = -220
                    reset = True
                elif self.direction == "OESTE" and self.x < L_MARGEN:
                    target_x = 1350
                    reset = True
                elif self.direction == "SUR" and self.y > B_MARGEN:
                    target_y = -200
                    reset = True
                elif self.direction == "NORTE" and self.y < L_MARGEN:
                    target_y = 760
                    reset = True

                if reset:
                    self.canvas.move(self.tag, target_x - self.x, target_y - self.y)
                    self.x = target_x
                    self.y = target_y

                time.sleep(0.03)
            except Exception:
                break


# ══════════════════════════════════════════════════════
# SIDEBAR — TÍTULO, SUBTÍTULO Y LEYENDA
# ══════════════════════════════════════════════════════

def sep():
    """Línea separadora horizontal."""
    tk.Frame(sidebar, bg=SEPARADOR, height=2).pack(fill=tk.X, padx=14, pady=9)

def caja_leyenda(color, texto):
    f = tk.Frame(sidebar, bg=color, padx=9, pady=4)
    f.pack(fill=tk.X, padx=11, pady=2)
    tk.Label(f, text=texto, bg=color, fg="white",
             font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

def crear_sidebar(hilos_activos):
    # Ícono principal
    tk.Label(sidebar, text="🚦", bg=PANEL_BG,
             font=("Segoe UI Emoji", 44)).pack(pady=(20, 4))

    # Título
    tk.Label(sidebar, text="SIMULADOR\nDE TRÁFICO\nINTELIGENTE",
             bg=PANEL_BG, fg=COLOR_TITULO,
             font=("Segoe UI", 13, "bold"), justify=tk.CENTER).pack()

    sep()

    # Subtítulo / descripción
    tk.Label(sidebar,
             text="Intersección inteligente\ncon doble vía y\nsincronización de hilos",
             bg=PANEL_BG, fg=COLOR_SUBTITULO,
             font=("Segoe UI", 9), justify=tk.CENTER).pack(padx=8)

    sep()

    # Leyenda vehículos
    tk.Label(sidebar, text="▸  VEHÍCULOS",
             bg=PANEL_BG, fg=INFO_AZUL,
             font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=14)

    caja_leyenda("#2e86de", "🚗   Vehículo ligero")
    caja_leyenda("#e07b39", "🚛   Camión pesado")
    caja_leyenda("#d4ac0d", "🚕   Taxi")

    sep()

    # Leyenda semáforos
    tk.Label(sidebar, text="▸  SEMÁFOROS",
             bg=PANEL_BG, fg=INFO_AZUL,
             font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=14)

    caja_leyenda(INFO_ROJO,     "🔴   Rojo = STOP")
    caja_leyenda(INFO_AMARILLO, "🟡   Amarillo = PRECAUCIÓN")
    caja_leyenda(INFO_VERDE,    "🟢   Verde = AVANZAR")

    sep()

    # Info de hilos
    tk.Label(sidebar,
             text=f"⚡ Hilos activos: {hilos_activos}\n🔄 Ciclo automático",
             bg=PANEL_BG, fg=COLOR_SUBTITULO,
             font=("Segoe UI", 9), justify=tk.CENTER).pack()


# ══════════════════════════════════════════════════════
# ESCENARIO (carreteras, líneas, pasos peatonales)
# ══════════════════════════════════════════════════════

def dibujar_fondo():
    canvas.configure(bg=HIERBA)

    # Carreteras
    canvas.create_rectangle(0, RD_H_Y1, 1202, RD_H_Y2,
                            fill=CARRETERA, outline="")
    canvas.create_rectangle(RD_V_X1, 0, RD_V_X2, 680,
                            fill=CARRETERA, outline="")

    # Líneas divisorias horizontales
    for x in range(0, 1202, 60):
        canvas.create_line(x, CTR_H, x + 30, CTR_H,
                           fill=LINEA_VIAL, width=3)

    # Líneas divisorias verticales
    for y in range(0, 680, 60):
        canvas.create_line(CTR_V, y, CTR_V, y + 30,
                           fill=LINEA_VIAL, width=3)

    # Pasos peatonales horizontales (superior e inferior)
    for x in range(470, 750, 15):
        canvas.create_line(RD_V_X1, 222, RD_V_X2, 222,
                           fill=LINEA_VIAL, width=4)
        canvas.create_rectangle(x, 232, x + 8, 262,
                                fill=LINEA_VIAL, outline="")
        canvas.create_line(RD_V_X1, 470, RD_V_X2, 470,
                           fill=LINEA_VIAL, width=4)
        canvas.create_rectangle(x, 432, x + 8, 462,
                                fill=LINEA_VIAL, outline="")

    # Pasos peatonales verticales (izquierdo y derecho)
    for y in range(220, 472, 15):
        canvas.create_line(470, RD_H_Y1, 470, RD_H_Y2,
                           fill=LINEA_VIAL, width=4)
        canvas.create_rectangle(480, y, 512, y + 8,
                                fill=LINEA_VIAL, outline="")
        canvas.create_line(742, RD_H_Y1, 742, RD_H_Y2,
                           fill=LINEA_VIAL, width=4)
        canvas.create_rectangle(702, y, 734, y + 8,
                                fill=LINEA_VIAL, outline="")


# ══════════════════════════════════════════════════════
# INICIALIZACIÓN Y CONFIGURACIÓN CRÍTICA
# ══════════════════════════════════════════════════════

# 1. Dibujar escenario
dibujar_fondo()

# 2. Inicializar Semáforos en las 4 esquinas exteriores
SEM_X_L = RD_V_X1 - 54      # 456
SEM_X_R = RD_V_X2 + 10      # 712
SEM_Y_T = RD_H_Y1 - 132     # 128
SEM_Y_B = RD_H_Y2 + 10      # 440

sem_izq = Semaphore(canvas, SEM_X_L, SEM_Y_T, "→ ESTE", "horizontal")
sem_der = Semaphore(canvas, SEM_X_R, SEM_Y_B, "← OESTE", "horizontal")
sem_sup = Semaphore(canvas, SEM_X_R, SEM_Y_T, "↓ SUR", "vertical")
sem_inf = Semaphore(canvas, SEM_X_L, SEM_Y_B, "↑ NORTE", "vertical")

# 3. Control de semáforos
light_system = TrafficLightSystem(ventana, [sem_izq, sem_der, sem_sup, sem_inf])

# 4. Crear vehículos (subclases de threading.Thread)
todos_vehiculos = []

def crear_y_arrancar_vehiculos():
    sep_h = GAP + 50   # 156px entre centros horizontales
    sep_v = GAP + 40   # 146px entre centros verticales

    # Horizontal → (ESTE)
    for i, emoji in enumerate(EMOJIS_ESTE):
        v = Vehicle(canvas, -sep_h * (i + 1), CARRIL_ESTE, emoji, "ESTE", light_system, todos_vehiculos)
        v.start()

    # Horizontal ← (OESTE)
    for i, emoji in enumerate(EMOJIS_OESTE):
        v = Vehicle(canvas, 1202 + sep_h * i, CARRIL_OESTE, emoji, "OESTE", light_system, todos_vehiculos)
        v.start()

    # Vertical ↓ (SUR)
    for i, emoji in enumerate(EMOJIS_SUR):
        v = Vehicle(canvas, CARRIL_SUR, -sep_v * (i + 1), emoji, "SUR", light_system, todos_vehiculos)
        v.start()

    # Vertical ↑ (NORTE)
    for i, emoji in enumerate(EMOJIS_NORTE):
        v = Vehicle(canvas, CARRIL_NORTE, 680 + sep_v * i, emoji, "NORTE", light_system, todos_vehiculos)
        v.start()

crear_y_arrancar_vehiculos()

# 5. Crear el sidebar dinámico (con número real de hilos de vehículos)
crear_sidebar(hilos_activos=len(todos_vehiculos))

# 6. Iniciar ciclo automático de semáforos
light_system.iniciar_ciclo()

# Iniciar bucle principal de interfaz gráfica
ventana.mainloop()