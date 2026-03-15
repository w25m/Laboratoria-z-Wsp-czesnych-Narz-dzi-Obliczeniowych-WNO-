import scipy.io
import numpy as np
import matplotlib.pyplot as plt


# Usunąłem importy z test4, bo nie są potrzebne do działania tego skryptu

def idw(x, y, z, xx_grid, yy_grid):
    x_flat = xx_grid.ravel()
    y_flat = yy_grid.ravel()

    # POPRAWKA: Nawiasy były źle ustawione.
    # Było: x[np.newaxis,:]**2 (kwadrat tylko drugiej liczby)
    # Powinno być: ( ... - ... )**2 (kwadrat różnicy)
    dist_sq = (x_flat[:, np.newaxis] - x[np.newaxis, :]) ** 2 + \
              (y_flat[:, np.newaxis] - y[np.newaxis, :]) ** 2

    dist = np.sqrt(dist_sq)
    dist[dist == 0] = 1e-10

    weights = 1 / (dist ** 4)

    num = np.sum(weights * z, axis=1)
    den = np.sum(weights, axis=1)

    z_result = num / den
    return z_result.reshape(xx_grid.shape)


# --- Ładowanie danych ---
load = scipy.io.loadmat('data_map.mat')
dane = load['data_map']
x = dane[:, 0]
y = dane[:, 1]
z = dane[:, 2]

# --- KROK 1: Tworzenie siatki (Grid) ---
SIZE = 100  # Rozdzielczość siatki (im więcej, tym gładszy wykres, ale wolniej)
xi = np.linspace(min(x), max(x), SIZE)
yi = np.linspace(min(y), max(y), SIZE)
xx, yy = np.meshgrid(xi, yi)

# --- KROK 2: Obliczanie interpolacji ---
print("Obliczam interpolację...")
z_final = idw(x, y, z, xx, yy)

# --- KROK 3: Rysowanie ---
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Rysowanie powierzchni interpolowanej
# alpha=0.6 sprawia, że wykres jest półprzezroczysty i widać punkty pod spodem
surf = ax.plot_surface(xx, yy, z_final, cmap='viridis', alpha=0.6, linewidth=0)

# Rysowanie oryginalnych punktów (krzyżyki)
ax.scatter(x, y, z, marker='x', c='r', s=50, label='Punkty pomiarowe')

ax.set_title("Interpolacja IDW")
ax.legend()
plt.show()