import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse

typ_krzywej = 'h'  # h - wewnątrz, e - na zewnątrz

a = 24  # szerokosc elipsy
b = 15  # wysokosc elipsy
r = 2.5  # promien kola w srodku
d = 5.0  # dlugosc promienia

def get_ellipse_state(t, a, b): #Zwraca pubkt styku z elipsa w chwili t
    x = a * np.cos(t)
    y = b * np.sin(t)
    dx = -a * np.sin(t)
    dy = b * np.cos(t)
    norm_angle = np.arctan2(dy, dx) - np.pi / 2
    speed = np.sqrt(dx ** 2 + dy ** 2)
    return x, y, norm_angle, speed


# Konfiguracja
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

#Skalowanie osi + kierunek
if typ_krzywej == 'h':
    title = f'Hypocykloida na Elipsie'
    limit = a + max(r, d) + 2
    offset_sign = -1
    roll_dir = -1
elif typ_krzywej == 'e':
    title = f'Epicykloida na Elipsie'
    limit = a + r + d + 2
    offset_sign = 1
    roll_dir = 1
else:
    raise ValueError("typ_krzywej musi być 'h' lub 'e'")

ax.set_title(title, fontsize=12, fontweight='bold')
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)

# Rysowanie elipsy
ax.add_patch(Ellipse((0, 0), 2 * a, 2 * b, fill=False, color='blue', linewidth=2, label='Elipsa'))

# Elementy animowane
trail, = ax.plot([], [], 'r-', linewidth=1, label='Ślad')

# Kolo toczace sie
circle_rolling = plt.Circle((0, 0), r, fill=False, color='green', linewidth=2, linestyle='--',
                            label='Koło rysujące')
ax.add_patch(circle_rolling)

# Wizualizacja promienia
radius_line, = ax.plot([], [], 'purple', linewidth=2, label='Promień wodzący')
point, = ax.plot([], [], 'ro', markersize=6, label='Punkt rysujący')
center_point, = ax.plot([], [], 'go', markersize=4)

ax.legend(loc='upper right')

# Na punkty traila
trail_x = []
trail_y = []


def init():
    trail.set_data([], [])
    radius_line.set_data([], [])
    point.set_data([], [])
    center_point.set_data([], [])
    trail_x.clear()
    trail_y.clear()
    return trail, circle_rolling, radius_line, point, center_point

dt = 0.05

# Zmienne stanu
s_accum = 0.0
last_t = 0.0

def data_gen():
    t = 0.0
    while True:
        yield t
        t += dt


def animate(t):
    global s_accum, last_t

    current_dt = t - last_t
    last_t = t
    if current_dt < 0: current_dt = dt

    # Zdobywa punkty styku z elipsa
    ex, ey, norm_angle, speed = get_ellipse_state(t, a, b)

    # Oblicza droge
    ds = speed * current_dt
    s_accum += ds

    # Oblicza pozycje srodka kola
    xc = ex + offset_sign * r * np.cos(norm_angle)
    yc = ey + offset_sign * r * np.sin(norm_angle)
    circle_rolling.center = (xc, yc)


    # Obliczanie kata obrotu
    theta_roll = (s_accum / r) * roll_dir
    theta_total = norm_angle + np.pi + theta_roll

    # Polozenie koncowki promienia
    xp = xc + d * np.cos(theta_total)
    yp = yc + d * np.sin(theta_total)

    # Aktualizacja list
    trail_x.append(xp)
    trail_y.append(yp)

    trail.set_data(trail_x, trail_y)
    # Rysowanie
    radius_line.set_data([xc, xp], [yc, yp])
    point.set_data([xp], [yp])
    center_point.set_data([xc], [yc])

    return trail, circle_rolling, radius_line, point, center_point


anim = FuncAnimation(fig, animate, frames=data_gen, init_func=init,
                     interval=20, blit=True, save_count=100, cache_frame_data=False)

plt.show()