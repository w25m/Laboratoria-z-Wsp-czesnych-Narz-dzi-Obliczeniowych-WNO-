import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

typ_krzywej = 'e'  # h- hipo e - epi


def hipocykloida(R, r, t):
    """Oblicza współrzędne hipocykloidy"""
    x = (R - r) * np.cos(t) + r * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - r * np.sin((R - r) / r * t)
    return x, y


def epicykloida(R, r, t):
    """Oblicza współrzędne epicykloidy"""
    x = (R + r) * np.cos(t) - r * np.cos((R + r) / r * t)
    y = (R + r) * np.sin(t) - r * np.sin((R + r) / r * t)
    return x, y


# Parametry
R = 8  # promień okręgu bazowego
r = 2  # "promień" kwadratu (od środka do wierzchołka)

# Tworzenie wykresu
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

# Wybór parametrów w zależności od typu krzywej
if typ_krzywej == 'h':
    title = f'Animacja Hipocykloidy z Kwadratem (R={R}, r={r})'
    xlim = (-R - 2, R + 2)
    ylim = (-R - 2, R + 2)
    func = hipocykloida
    center_calc = lambda t: ((R - r) * np.cos(t), (R - r) * np.sin(t))
elif typ_krzywej == 'e':
    title = f'Animacja Epicykloidy z Kwadratem (R={R}, r={r})'
    xlim = (-R - r - 2, R + r + 2)
    ylim = (-R - r - 2, R + r + 2)
    func = epicykloida
    center_calc = lambda t: ((R + r) * np.cos(t), (R + r) * np.sin(t))
else:
    raise ValueError("typ_krzywej musi być 'h' lub 'e'")

ax.set_title(title, fontsize=14, fontweight='bold')
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# Okrąg bazowy (stały)
circle_base = plt.Circle((0, 0), R, fill=False, color='blue', linewidth=2, label='Okrąg bazowy')
ax.add_patch(circle_base)

# Elementy animowane
trail, = ax.plot([], [], 'r-', linewidth=2, label=typ_krzywej.capitalize())

# ZMIANA: Zamiast circle_rolling używamy plot do rysowania kwadratu
square_plot, = ax.plot([], [], 'g-', linewidth=2, label='Kwadrat toczący się')

radius_line, = ax.plot([], [], 'purple', linewidth=2, label='Promień wodzący')
point, = ax.plot([], [], 'ro', markersize=8, label='Punkt kreślący')
center_point, = ax.plot([], [], 'go', markersize=6)

ax.legend(loc='upper right')

# Dane dla animacji
frames = 200
t_vals = np.linspace(0, 2 * np.pi * 3, frames)

# Listy do przechowywania śladu
trail_x = []
trail_y = []


def init():
    """Inicjalizacja animacji"""
    trail.set_data([], [])
    square_plot.set_data([], [])  # Reset kwadratu
    radius_line.set_data([], [])
    point.set_data([], [])
    center_point.set_data([], [])
    trail_x.clear()
    trail_y.clear()
    return trail, square_plot, radius_line, point, center_point


def animate(frame):
    """Funkcja animacji wywoływana dla każdej klatki"""
    t = t_vals[frame]

    # 1. Pozycja środka kwadratu
    xc, yc = center_calc(t)

    # 2. Pozycja punktu kreślącego (jeden z wierzchołków)
    xp, yp = func(R, r, t)

    # 3. Obliczanie wierzchołków kwadratu
    # Wektor od środka do punktu kreślącego (to jest połowa przekątnej kwadratu)
    vx = xp - xc
    vy = yp - yc

    # Tworzymy 4 rogi poprzez obracanie wektora o 90 stopni
    # (x, y) -> (-y, x) to obrót o 90 stopni

    # Róg 1 (punkt kreślący)
    p1x, p1y = xc + vx, yc + vy
    # Róg 2
    p2x, p2y = xc - vy, yc + vx
    # Róg 3
    p3x, p3y = xc - vx, yc - vy
    # Róg 4
    p4x, p4y = xc + vy, yc - vx

    # Składamy współrzędne w listę (zamykamy pętlę wracając do p1)
    sq_x = [p1x, p2x, p3x, p4x, p1x]
    sq_y = [p1y, p2y, p3y, p4y, p1y]

    # Aktualizacja kwadratu
    square_plot.set_data(sq_x, sq_y)

    # Aktualizacja śladu
    trail_x.append(xp)
    trail_y.append(yp)
    trail.set_data(trail_x, trail_y)

    # Promień wodzący (od środka do punktu rysującego)
    radius_line.set_data([xc, xp], [yc, yp])

    # Punkty
    point.set_data([xp], [yp])
    center_point.set_data([xc], [yc])

    return trail, square_plot, radius_line, point, center_point


# Utworzenie animacji
anim = FuncAnimation(fig, animate, init_func=init, frames=frames,
                     interval=30, blit=True, repeat=True)

plt.show()