import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# 1. Konfiguracja i ładowanie modelu CLIP
# Używamy wersji 'base', jest lżejsza, ale wystarczająco dokładna.
model_name = "openai/clip-vit-base-patch32"
print(f"Ładowanie modelu: {model_name}...")
model = CLIPModel.from_pretrained(model_name)
processor = CLIPProcessor.from_pretrained(model_name)


# 2. Funkcja do ekstrakcji wektora cech z pojedynczego obrazu
def get_image_embedding(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        # Przetworzenie obrazu do formatu akceptowanego przez sieć
        inputs = processor(images=image, return_tensors="pt")

        # Wyłączenie liczenia gradientów (nie trenujemy sieci, tylko używamy)
        with torch.no_grad():
            # Pobranie cech obrazu (image_features)
            outputs = model.get_image_features(**inputs)

        # Zwracamy wektor jako tablicę numpy (usuwamy zbędne wymiary)
        return outputs.squeeze().numpy()
    except Exception as e:
        print(f"Błąd przy pliku {image_path}: {e}")
        return None


# 3. Wczytanie danych
# ZMIEŃ TĘ ŚCIEŻKĘ na folder ze swoimi obrazami (np. *.jpg, *.png)
# Możesz też ręcznie podać listę plików: image_files = ["img1.jpg", "img2.jpg", ...]
sciezka_do_obrazow = "Final_images_dataset/*.jpg"
image_files = glob.glob(sciezka_do_obrazow)

# Dla testu, jeśli nie masz plików, odkomentuj poniższą linię, aby sprawdzić czy kod działa (będzie błąd braku plików, ale logika jest ok)
# if not image_files: print("Brak plików! Podaj poprawną ścieżkę.")

embeddings = []
valid_files = []

print(f"Przetwarzanie {len(image_files)} obrazów...")

for file in image_files:
    emb = get_image_embedding(file)
    if emb is not None:
        embeddings.append(emb)
        valid_files.append(file)

if len(embeddings) < 2:
    print("Za mało danych do wygenerowania wykresu (potrzeba min. 2).")
    exit()

# Konwersja listy do macierzy numpy
X = np.array(embeddings)
print(f"Kształt macierzy cech: {X.shape}")  # Np. (100, 512)

# 4. Redukcja wymiarowości (t-SNE)
# CLIP zwraca wektory 512-wymiarowe. Musimy zrobić z nich 2D (x, y), żeby narysować wykres.
# t-SNE świetnie zachowuje lokalną strukturę klastrów.
print("Obliczanie t-SNE (redukcja do 2D)...")
n_components = 2
perplexity = min(30, len(embeddings) - 1)  # Perplexity musi być mniejsze niż liczba próbek
tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42, init='pca', learning_rate='auto')
X_embedded = tsne.fit_transform(X)

# 5. Wizualizacja
plt.figure(figsize=(10, 8))
plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c='blue', alpha=0.6, s=50)

plt.title(f"Wizualizacja wektorów CLIP dla {len(valid_files)} obrazów")
plt.xlabel("Wymiar t-SNE 1")
plt.ylabel("Wymiar t-SNE 2")
plt.grid(True, linestyle='--', alpha=0.3)

# Opcjonalnie: dodanie nazw plików do punktów (może być nieczytelne przy dużej ilości)
# for i, txt in enumerate(valid_files):
#     plt.annotate(os.path.basename(txt), (X_embedded[i, 0], X_embedded[i, 1]), fontsize=8)

plt.show()