import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parametry kół
R = 10  # promień okręgu bazowego
r = 3  # promień okręgu toczącego się
d = 4.0  # odległość punktu piszącego

# Parametry zębów
liczba_zebow_toczace = 12
wysokosc_zebow = 0.4
liczba_zebow_bazowe = int(liczba_zebow_toczace * (R / r))


# Funkcje matematyczne
def hipocykloida(R, r, d, t):
    x = (R - r) * np.cos(t) + d * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - d * np.sin((R - r) / r * t)
    return x, y


def epicykloida(R, r, d, t):
    x = (R + r) * np.cos(t) - d * np.cos((R + r) / r * t)
    y = (R + r) * np.sin(t) - d * np.sin((R + r) / r * t)
    return x, y


def stworz_kolo_zebate(promien, liczba_zebow, wysokosc_zebow, zeby_na_zewnatrz=True): #zwraca punkty okregu z zebami
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
ax.set_aspect('equal') #wymusza równe skale osi
ax.grid(True, alpha=0.3)#widoczność kratek

ax.set_title(f'Epicykloida i hipocyloida', fontsize=12, fontweight='bold')
limit = R + r + d + 2
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)#stawianie wartosci osi

# Koło bazowe
promien_bazy = R - wysokosc_zebow
gear_base_x, gear_base_y = stworz_kolo_zebate(promien_bazy, liczba_zebow_bazowe, wysokosc_zebow,zeby_na_zewnatrz=True)
ax.plot(gear_base_x, gear_base_y, 'k-', linewidth=0.5, label='Koło bazowe')

# Trail rysowanie hipo
trail_hypo, = ax.plot([], [], 'r-', linewidth=0.5, label='Hipocykloida')
gear_rolling_hypo, = ax.plot([], [], 'r--', linewidth=0.5, alpha=0.7)
# Punkt rysowanie hipo
point_hypo, = ax.plot([], [], 'ro', markersize=6)
radius_line_hypo, = ax.plot([], [], 'r-', linewidth=0.5, alpha=0.5)
# Trail rysowanie epi
trail_epi, = ax.plot([], [], 'b-', linewidth=0.5, label='Epicykloida')
gear_rolling_epi, = ax.plot([], [], 'b--', linewidth=0.5, alpha=0.7)
# Punkt rysowanie epi
point_epi, = ax.plot([], [], 'bo', markersize=6)
radius_line_epi, = ax.plot([], [], 'b-', linewidth=0.5, alpha=0.5)

ax.legend(loc='upper right', fontsize=9)

# Kolo toczace
promien_wizualny_toczacego = r - wysokosc_zebow
gx, gy = stworz_kolo_zebate(promien_wizualny_toczacego, liczba_zebow_toczace, wysokosc_zebow, zeby_na_zewnatrz=True)
offset_angle = np.pi / liczba_zebow_toczace
gear_rolling_base_x = gx * np.cos(offset_angle) - gy * np.sin(offset_angle)
gear_rolling_base_y = gx * np.sin(offset_angle) + gy * np.cos(offset_angle)

# Listy na traila
trail_hypo_x, trail_hypo_y = [], []
trail_epi_x, trail_epi_y = [], []


def animate(frame):
    t = frame * 0.05

    # Obliczenia dla hipo
    cx_h = (R - r) * np.cos(t)
    cy_h = (R - r) * np.sin(t) #przesuniecie srodka okregu
    rot_h = -(R - r) / r * t
    cos_h, sin_h = np.cos(rot_h), np.sin(rot_h) #obrot kola
    gh_x = gear_rolling_base_x * cos_h - gear_rolling_base_y * sin_h + cx_h
    gh_y = gear_rolling_base_x * sin_h + gear_rolling_base_y * cos_h + cy_h
    px_h, py_h = hipocykloida(R, r, d, t)

    gear_rolling_hypo.set_data(gh_x, gh_y)
    trail_hypo_x.append(px_h)
    trail_hypo_y.append(py_h)
    trail_hypo.set_data(trail_hypo_x, trail_hypo_y)
    point_hypo.set_data([px_h], [py_h])
    radius_line_hypo.set_data([cx_h, px_h], [cy_h, py_h])

    # Obliczenia dla epi
    dist_e = R + r - wysokosc_zebow
    cx_e = dist_e * np.cos(t)
    cy_e = dist_e * np.sin(t)

    rot_e = -(R + r) / r * t
    cos_e, sin_e = np.cos(rot_e), np.sin(rot_e)
    ge_x = gear_rolling_base_x * cos_e - gear_rolling_base_y * sin_e + cx_e
    ge_y = gear_rolling_base_x * sin_e + gear_rolling_base_y * cos_e + cy_e
    px_e, py_e = epicykloida(R, r, d, t)

    gear_rolling_epi.set_data(ge_x, ge_y)
    trail_epi_x.append(px_e)
    trail_epi_y.append(py_e)
    trail_epi.set_data(trail_epi_x, trail_epi_y)
    point_epi.set_data([px_e], [py_e])
    radius_line_epi.set_data([cx_e, px_e], [cy_e, py_e])

    return trail_hypo, gear_rolling_hypo, point_hypo, radius_line_hypo, trail_epi, gear_rolling_epi, point_epi, radius_line_epi


anim = FuncAnimation(fig, animate, interval=30, blit=True, cache_frame_data=False)

plt.show()