import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

typ_krzywej = 'hipocykloida'  # 'hipocykloida' lub 'epicykloida'

# Parametry kół
R = 10  # promień okręgu bazowego
r = 2  # promień okręgu toczącego się

# Parametry zębów
liczba_zebow_bazowe = 32  # liczba zębów koła bazowego
liczba_zebow_toczace = 8  # liczba zębów koła toczącego się
wysokosc_zebow = 0.3  # wysokość zębów

def hipocykloida(R, r, t):
    x = (R - r) * np.cos(t) + r * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - r * np.sin((R - r) / r * t)
    return x, y


def epicykloida(R, r, t):
    x = (R + r) * np.cos(t) - r * np.cos((R + r) / r * t)

    y = (R + r) * np.sin(t) - r * np.sin((R + r) / r * t)
    return x, y


def stworz_kolo_zebate(promien, liczba_zebow, wysokosc_zebow, zeby_na_zewnatrz=True):

    angles = []
    radii = []

    angles = []
    radii = []
    for i in range(liczba_zebow):
        theta_start = 2 * np.pi * i / liczba_zebow
        theta_mid = 2 * np.pi * (i + 0.5) / liczba_zebow
        theta_end = 2 * np.pi * (i + 1) / liczba_zebow

        if zeby_na_zewnatrz:
            angles.extend([theta_start, theta_mid, theta_end])
            radii.extend([promien, promien + wysokosc_zebow, promien])
        else:
            angles.extend([theta_start, theta_mid, theta_end])
            radii.extend([promien, promien - wysokosc_zebow, promien])

    angles.append(angles[0])
    radii.append(radii[0])
    x = np.array(radii) * np.cos(angles)
    y = np.array(radii) * np.sin(angles)
    return x, y


# Tworzenie wykresu
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect('equal') # równe osie
ax.grid(True, alpha=0.3) #widocznosc kratek

# Wybór parametrów w zależności od typu krzywej
if typ_krzywej == 'hipocykloida':
    title = f'Animacja Hipocykloidy - Koła Zębate\n(R={R}, r={r}, zęby: {liczba_zebow_bazowe}/{liczba_zebow_toczace})'
    xlim = (-R - 2, R + 2)
    ylim = (-R - 2, R + 2)
    func = hipocykloida
    center_calc = lambda t: ((R - r) * np.cos(t), (R - r) * np.sin(t))
elif typ_krzywej == 'epicykloida':
    title = f'Animacja Epicykloidy - Koła Zębate\n(R={R}, r={r}, zęby: {liczba_zebow_bazowe}/{liczba_zebow_toczace})'
    xlim = (-R - r - 2, R + r + 2)
    ylim = (-R - r - 2, R + r + 2)
    func = epicykloida
    center_calc = lambda t: ((R + r) * np.cos(t), (R + r) * np.sin(t))
else:
    raise ValueError("typ_krzywej musi być 'hipocykloida' lub 'epicykloida'")

ax.set_title(title, fontsize=12, fontweight='bold')
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# Koło bazowe (zębate, stałe)
if typ_krzywej == 'epicykloida':
    # Dla epicykloidy
    gear_base_x, gear_base_y = stworz_kolo_zebate(R, liczba_zebow_bazowe, wysokosc_zebow, zeby_na_zewnatrz=False) #tworzy współrzędne tego kola
else:
    # Dla hipocykloidy
    gear_base_x, gear_base_y = stworz_kolo_zebate(R, liczba_zebow_bazowe, wysokosc_zebow, zeby_na_zewnatrz=True)

gear_base, = ax.plot(gear_base_x, gear_base_y, 'b-', linewidth=2, label='Koło bazowe')

# Elementy animowane
trail, = ax.plot([], [], 'r-', linewidth=2, label=typ_krzywej.capitalize())

# Koło głowne
gear_rolling, = ax.plot([], [], 'g--', linewidth=2, label='Koło toczące się')

radius_line, = ax.plot([], [], 'purple', linewidth=2, label='Promień wodzący')
point, = ax.plot([], [], 'ro', markersize=8, label='Punkt kreślący')
center_point, = ax.plot([], [], 'go', markersize=6)

ax.legend(loc='upper right', fontsize=9)

# Dane dla animacji
frames = 200
t_vals = np.linspace(0, 2 * np.pi * 3, frames) # generuje wartosc t dla kazdej klatki

# Listy do przechowywania śladu
trail_x = []
trail_y = []

# Tworzenie koła poruszającego się
gear_rolling_base_x, gear_rolling_base_y = stworz_kolo_zebate(r, liczba_zebow_toczace, wysokosc_zebow,
                                                              zeby_na_zewnatrz=True)


def init():
    trail.set_data([], [])
    gear_rolling.set_data([], [])
    radius_line.set_data([], [])
    point.set_data([], [])
    center_point.set_data([], [])
    trail_x.clear()
    trail_y.clear()
    return trail, gear_rolling, radius_line, point, center_point


def animate(frame):
    t = t_vals[frame] #pobiera wartosc t dla klatki

    # Pozycja środka okręgu toczącego się
    x_center, y_center = center_calc(t)

    # Kąt obrotu koła toczącego się (żeby się nie ślizgało)
    if typ_krzywej == 'hipocykloida':
        rotation_angle = -(R - r) / r * t
    else:  # epicykloida
        rotation_angle = -(R + r) / r * t

    # Obrót i przesunięcie koła toczącego się
    cos_rot = np.cos(rotation_angle)
    sin_rot = np.sin(rotation_angle)
    gear_x = gear_rolling_base_x * cos_rot - gear_rolling_base_y * sin_rot + x_center
    gear_y = gear_rolling_base_x * sin_rot + gear_rolling_base_y * cos_rot + y_center

    gear_rolling.set_data(gear_x, gear_y)

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

    return trail, gear_rolling, radius_line, point, center_point


# Utworzenie animacji
anim = FuncAnimation(fig, animate, init_func=init, frames=frames,
                     interval=30, blit=True, repeat=True)

plt.show()