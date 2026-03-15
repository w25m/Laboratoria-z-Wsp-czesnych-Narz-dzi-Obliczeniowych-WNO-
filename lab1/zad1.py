import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

typ_krzywej = 'h'  # h- hipo e - epi

def hipocykloida(R, r, t):
    """
    Oblicza współrzędne hipocykloidy
    R - promień okręgu bazowego
    r - promień okręgu toczącego się
    t - parametr (kąt)
    """
    x = (R - r) * np.cos(t) + r * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - r * np.sin((R - r) / r * t)
    return x, y


def epicykloida(R, r, t):
    """
    Oblicza współrzędne epicykloidy
    R - promień okręgu bazowego
    r - promień okręgu toczącego się
    t - parametr (kąt)
    """
    x = (R + r) * np.cos(t) - r * np.cos((R + r) / r * t)
    y = (R + r) * np.sin(t) - r * np.sin((R + r) / r * t)
    return x, y


# Parametry
R = 8  # promień okręgu bazowego
r = 2  # promień okręgu toczącego się

# Tworzenie wykresu
fig, ax = plt.subplots(figsize=(8, 8)) # wielkosc okienka w calach
ax.set_aspect('equal') #ustawia równe skale osi
ax.grid(True, alpha=0.3) #przezroczystosc kratek

# Wybór parametrów w zależności od typu krzywej
if typ_krzywej == 'h':
    title = f'Animacja Hipocykloidy (R={R}, r={r})'
    xlim = (-R - 2, R + 2)
    ylim = (-R - 2, R + 2)
    func = hipocykloida
    center_calc = lambda t: ((R - r) * np.cos(t), (R - r) * np.sin(t))
elif typ_krzywej == 'e':
    title = f'Animacja Epicykloidy (R={R}, r={r})'
    xlim = (-R - r - 2, R + r + 2)
    ylim = (-R - r - 2, R + r + 2)
    func = epicykloida
    center_calc = lambda t: ((R + r) * np.cos(t), (R + r) * np.sin(t))
else:
    raise ValueError("typ_krzywej musi być 'hipocykloida' lub 'epicykloida'")

ax.set_title(title, fontsize=14, fontweight='bold')
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# Okrąg bazowy (stały)
circle_base = plt.Circle((0, 0), R, fill=False, color='blue', linewidth=2, label='Okrąg bazowy')
ax.add_patch(circle_base)

# Elementy animowane
trail, = ax.plot([], [], 'r-', linewidth=2, label=typ_krzywej.capitalize())
circle_rolling = plt.Circle((0, 0), r, fill=False, color='green', linewidth=2, linestyle='--',
                            label='Okrąg toczący się')
ax.add_patch(circle_rolling)
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
    radius_line.set_data([], [])
    point.set_data([], [])
    center_point.set_data([], [])
    trail_x.clear()
    trail_y.clear()
    return trail, circle_rolling, radius_line, point, center_point


def animate(frame):
    """Funkcja animacji wywoływana dla każdej klatki"""
    t = t_vals[frame]

    # Pozycja środka okręgu toczącego się
    x_center, y_center = center_calc(t)
    circle_rolling.center = (x_center, y_center)

    # Pozycja punktu kreślącego
    x_point, y_point = func(R, r, t)

    # Aktualizacja śladu
    trail_x.append(x_point)
    trail_y.append(y_point)
    trail.set_data(trail_x, trail_y)

    # Promień wodzący
    radius_line.set_data([x_center, x_point], [y_center, y_point])

    # Punkty
    point.set_data([x_point], [y_point])
    center_point.set_data([x_center], [y_center])

    return trail, circle_rolling, radius_line, point, center_point


# Utworzenie animacji
anim = FuncAnimation(fig, animate, init_func=init, frames=frames,
                     interval=30, blit=True, repeat=True)

plt.show()