"""Aurora Focus — temporizador Pomodoro con anillo de luz y partículas.

Sin dependencias externas: solo tkinter (incluido con Python).
Ejecutar:  python aurora_focus.py

Controles:  espacio = iniciar/pausar · R = reiniciar · +/− ajustan la duración
"""

import math
import random
import time
import tkinter as tk

try:
    import winsound
except ImportError:
    winsound = None

W, H = 460, 640
CX, CY = W // 2, 270
RING_R = 150

BG = "#0a0d16"
FG = "#e5eaf5"
MUTED = "#7c8598"

PALETTES = {
    "focus": ("#22d3ee", "#60a5fa", "#818cf8", "#c084fc"),
    "break": ("#34d399", "#6ee7b7", "#2dd4bf", "#facc15"),
}
ACCENT = {"focus": "#60a5fa", "break": "#34d399"}
WARN = "#fbbf24"
DANGER = "#f43f5e"


def mix(c1, c2, t):
    """Interpola dos colores hex; t=0 devuelve c1, t=1 devuelve c2."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return "#%02x%02x%02x" % (
        round(r1 + (r2 - r1) * t),
        round(g1 + (g2 - g1) * t),
        round(b1 + (b2 - b1) * t),
    )


def rounded_rect(canvas, x1, y1, x2, y2, r, **kw):
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


class Orbital:
    """Partícula que orbita alrededor del anillo con oscilación radial."""

    def __init__(self, palette):
        self.angle = random.uniform(0, math.tau)
        self.speed = random.uniform(0.12, 0.55) * random.choice((1, 1, 1, -1))
        self.base_r = RING_R + random.uniform(-32, 44)
        self.wobble_amp = random.uniform(5, 18)
        self.wobble_freq = random.uniform(0.3, 1.3)
        self.phase = random.uniform(0, math.tau)
        self.size = random.uniform(1.2, 3.4)
        self.color = random.choice(palette)

    def update(self, dt, mult):
        self.angle += self.speed * mult * dt

    def render(self, canvas, t):
        r = self.base_r + self.wobble_amp * math.sin(t * self.wobble_freq + self.phase)
        x = CX + r * math.cos(self.angle)
        y = CY + r * math.sin(self.angle)
        twinkle = 0.5 + 0.5 * math.sin(t * 1.7 + self.phase)
        color = mix(BG, self.color, 0.30 + 0.70 * twinkle)
        s = self.size
        canvas.create_oval(x - s, y - s, x + s, y + s, fill=color, outline="")


class AuroraFocus:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Aurora Focus")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.focus_min = 25
        self.mode = "focus"        # 'focus' | 'break'
        self.state = "idle"        # 'idle' | 'running' | 'paused'
        self.remaining = self.focus_min * 60.0
        self.cycles = 0

        self.orbitals = [Orbital(PALETTES["focus"]) for _ in range(70)]
        self.stars = [
            (random.uniform(0, W), random.uniform(0, H),
             random.uniform(0.5, 1.6), random.uniform(0, math.tau))
            for _ in range(55)
        ]
        self.burst = []

        self.buttons = []
        self.hover = None
        self.t0 = time.monotonic()
        self.last = self.t0

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.root.bind("<space>", lambda e: self.start_pause())
        self.root.bind("r", lambda e: self.reset())
        self.root.bind("R", lambda e: self.reset())
        self.root.bind("+", lambda e: self.adjust(5))
        self.root.bind("-", lambda e: self.adjust(-5))

        self.tick()

    # ------------------------------------------------------------- lógica

    @property
    def break_min(self):
        return max(3, round(self.focus_min / 5))

    def total(self):
        mins = self.focus_min if self.mode == "focus" else self.break_min
        return mins * 60.0

    def start_pause(self):
        if self.state == "running":
            self.state = "paused"
        else:
            self.state = "running"

    def reset(self):
        self.mode = "focus"
        self.state = "idle"
        self.remaining = self.total()
        self.retint()

    def adjust(self, delta):
        if self.state == "idle" and self.mode == "focus":
            self.focus_min = max(5, min(60, self.focus_min + delta))
            self.remaining = self.total()

    def complete(self):
        self.spawn_burst()
        if winsound:
            winsound.MessageBeep()
        else:
            self.root.bell()
        if self.mode == "focus":
            self.cycles += 1
            self.mode = "break"
            self.remaining = self.total()
            self.state = "running"   # el descanso arranca solo
        else:
            self.mode = "focus"
            self.remaining = self.total()
            self.state = "idle"      # el siguiente enfoque espera tu señal
        self.retint()

    def retint(self):
        palette = PALETTES[self.mode]
        for p in self.orbitals:
            p.color = random.choice(palette)

    def spawn_burst(self):
        palette = PALETTES[self.mode]
        for _ in range(90):
            a = random.uniform(0, math.tau)
            speed = random.uniform(50, 260)
            self.burst.append({
                "x": CX + RING_R * math.cos(a),
                "y": CY + RING_R * math.sin(a),
                "vx": math.cos(a) * speed + random.uniform(-40, 40),
                "vy": math.sin(a) * speed + random.uniform(-40, 40),
                "life": 1.0,
                "decay": random.uniform(0.5, 1.1),
                "size": random.uniform(1.5, 3.5),
                "color": random.choice(palette),
            })

    # ---------------------------------------------------------- animación

    def tick(self):
        now = time.monotonic()
        dt = min(now - self.last, 0.05)
        self.last = now

        if self.state == "running":
            self.remaining -= dt
            if self.remaining <= 0:
                self.complete()

        frac = max(0.0, self.remaining / self.total())
        if self.state == "running":
            mult = 1.0 + (1.0 - frac) * 1.6
            if frac < 0.12:
                mult += 1.5
        else:
            mult = 0.45

        for p in self.orbitals:
            p.update(dt, mult)

        for b in self.burst:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            b["vx"] *= 0.985
            b["vy"] *= 0.985
            b["life"] -= b["decay"] * dt
        self.burst = [b for b in self.burst if b["life"] > 0]

        self.draw(now - self.t0, frac)
        self.root.after(16, self.tick)

    def ring_color(self, frac):
        color = ACCENT[self.mode]
        if self.state != "idle" and self.mode == "focus":
            if frac < 0.35:
                color = mix(color, WARN, (0.35 - frac) / 0.23)
            if frac < 0.12:
                color = mix(WARN, DANGER, (0.12 - frac) / 0.12)
        return color

    def draw(self, t, frac):
        c = self.canvas
        c.delete("all")
        self.buttons = []

        # estrellas de fondo
        for x, y, s, ph in self.stars:
            glow = 0.18 + 0.22 * (0.5 + 0.5 * math.sin(t * (0.3 + s * 0.4) + ph))
            c.create_oval(x - s, y - s, x + s, y + s, fill=mix(BG, FG, glow), outline="")

        # anillo base tenue
        box = (CX - RING_R, CY - RING_R, CX + RING_R, CY + RING_R)
        c.create_oval(box, outline=mix(BG, ACCENT[self.mode], 0.16), width=10)

        # arco de progreso con halo (3 capas)
        color = self.ring_color(frac)
        extent = -359.9 * frac
        if frac > 0.001:
            for width, k in ((18, 0.16), (10, 0.45), (4, 1.0)):
                c.create_arc(box, start=90, extent=extent, style="arc",
                             outline=mix(BG, color, k), width=width)
            # punta brillante del arco
            tip = math.radians(90 + extent)
            tx = CX + RING_R * math.cos(tip)
            ty = CY - RING_R * math.sin(tip)
            for rad, k in ((7, 0.35), (4, 0.8), (2.2, 1.0)):
                c.create_oval(tx - rad, ty - rad, tx + rad, ty + rad,
                              fill=mix(BG, color, k), outline="")

        # partículas orbitales
        for p in self.orbitals:
            p.render(c, t)

        # explosión de cierre de ciclo
        for b in self.burst:
            k = max(0.0, b["life"])
            s = b["size"] * (0.5 + 0.5 * k)
            c.create_oval(b["x"] - s, b["y"] - s, b["x"] + s, b["y"] + s,
                          fill=mix(BG, b["color"], k), outline="")

        # textos centrales
        mode_label = "E N F O Q U E" if self.mode == "focus" else "D E S C A N S O"
        c.create_text(CX, CY - 58, text=mode_label, fill=mix(BG, ACCENT[self.mode], 0.9),
                      font=("Segoe UI", 11, "bold"))

        mins, secs = divmod(max(0, int(math.ceil(self.remaining))), 60)
        pulse = 2 * math.sin(t * 2.5) if self.state == "running" else 0
        c.create_text(CX, CY - 2, text=f"{mins:02d}:{secs:02d}", fill=FG,
                      font=("Consolas", 46 + round(pulse), "bold"))

        status = ""
        if self.state == "paused":
            status = "en pausa"
        elif self.state == "idle":
            status = "¡buen trabajo! ¿otro ciclo?" if self.cycles else "pulsa iniciar o espacio"
        elif self.mode == "break":
            status = "respira, estira, hidrátate"
        c.create_text(CX, CY + 48, text=status, fill=MUTED, font=("Segoe UI", 10))

        # fila de duración
        y = 470
        adjustable = self.state == "idle" and self.mode == "focus"
        c.create_text(CX, y, text=f"{self.focus_min} min enfoque · {self.break_min} min descanso",
                      fill=MUTED if not adjustable else mix(MUTED, FG, 0.3),
                      font=("Segoe UI", 10))
        for sign, x in (("−", CX - 118), ("+", CX + 118)):
            key = f"adj{sign}"
            base = mix(BG, MUTED, 0.25 if adjustable else 0.10)
            if adjustable and self.hover == key:
                base = mix(BG, ACCENT[self.mode], 0.45)
            c.create_oval(x - 14, y - 14, x + 14, y + 14, fill=base, outline="")
            c.create_text(x, y - 1, text=sign, fill=FG if adjustable else MUTED,
                          font=("Segoe UI", 13, "bold"))
            if adjustable:
                self.buttons.append((x - 14, y - 14, x + 14, y + 14, key,
                                     lambda s=sign: self.adjust(5 if s == "+" else -5)))

        # botones principales
        y1, y2 = 505, 549
        accent = ACCENT[self.mode]
        label = {"idle": "▶  Iniciar", "running": "⏸  Pausa", "paused": "▶  Continuar"}[self.state]

        fill = mix(BG, accent, 0.85 if self.hover == "main" else 0.7)
        rounded_rect(c, CX - 146, y1, CX + 24, y2, 14, fill=fill, outline="")
        c.create_text(CX - 61, (y1 + y2) / 2, text=label, fill="#0b1020",
                      font=("Segoe UI", 12, "bold"))
        self.buttons.append((CX - 146, y1, CX + 24, y2, "main", self.start_pause))

        fill = mix(BG, MUTED, 0.35 if self.hover == "reset" else 0.18)
        rounded_rect(c, CX + 36, y1, CX + 146, y2, 14, fill=fill, outline="")
        c.create_text(CX + 91, (y1 + y2) / 2, text="Reiniciar", fill=FG,
                      font=("Segoe UI", 11))
        self.buttons.append((CX + 36, y1, CX + 146, y2, "reset", self.reset))

        # ciclos completados
        if self.cycles:
            dots = "●" * min(self.cycles, 8) + (f"  ×{self.cycles}" if self.cycles > 8 else "")
            c.create_text(CX, 582, text=f"ciclos completados   {dots}",
                          fill=mix(BG, ACCENT["focus"], 0.65), font=("Segoe UI", 9))

        c.create_text(CX, 612, text="espacio: iniciar/pausar   ·   R: reiniciar   ·   +/−: duración",
                      fill=mix(BG, MUTED, 0.7), font=("Segoe UI", 8))

    # -------------------------------------------------------- interacción

    def on_click(self, event):
        for x1, y1, x2, y2, _key, action in self.buttons:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                action()
                return

    def on_motion(self, event):
        self.hover = None
        for x1, y1, x2, y2, key, _action in self.buttons:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.hover = key
                break
        self.canvas.config(cursor="hand2" if self.hover else "")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AuroraFocus().run()
