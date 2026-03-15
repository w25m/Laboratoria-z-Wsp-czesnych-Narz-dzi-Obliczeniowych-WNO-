import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

# 1. Konfiguracja i ładowanie modelu ViT-GPT2
# Model składa się z Vision Transformera (Enkoder) i GPT-2 (Dekoder)
model_name = "nlpconnect/vit-gpt2-image-captioning"
print(f"Ładowanie modelu: {model_name}...")

# Ładujemy cały model, ale będziemy używać głównie jego enkodera
model = VisionEncoderDecoderModel.from_pretrained(model_name)
feature_extractor = ViTImageProcessor.from_pretrained(model_name)

# Ustawienie urządzenia (GPU jeśli dostępne, inaczej CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)


# 2. Funkcja do ekstrakcji wektora z Enkodera (ViT)
def get_vit_gpt2_embedding(image_path):
    try:
        image = Image.open(image_path).convert("RGB")

        # Przygotowanie obrazu (skalowanie, normalizacja)
        pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        with torch.no_grad():
            # KLUCZOWY MOMENT:
            # Nie używamy model.generate() (które robi tekst).
            # Używamy model.encoder(), aby dostać matematyczną reprezentację obrazu.
            encoder_outputs = model.encoder(pixel_values)

            # last_hidden_state ma wymiary: [batch_size, sequence_length, hidden_size]
            # Np. [1, 197, 768]. Musimy to spłaszczyć do jednego wektora.
            # Bierzemy wektor z indeksu 0 (odpowiednik tokenu [CLS] w BERT/ViT),
            # który reprezentuje cały obraz.
            image_embedding = encoder_outputs.last_hidden_state[:, 0, :]

        return image_embedding.cpu().numpy().flatten()
    except Exception as e:
        print(f"Błąd przy pliku {image_path}: {e}")
        return None


# 3. Wczytywanie danych
# ZMIEŃ ŚCIEŻKĘ na swój folder
sciezka_do_obrazow = "Final_images_dataset/*.jpg"
image_files = glob.glob(sciezka_do_obrazow)

embeddings = []
valid_files = []

print(f"Przetwarzanie {len(image_files)} obrazów...")

for file in image_files:
    emb = get_vit_gpt2_embedding(file)
    if emb is not None:
        embeddings.append(emb)
        valid_files.append(file)

if len(embeddings) < 2:
    print("Za mało danych. Wymagane minimum 2 obrazy.")
    exit()

X = np.array(embeddings)
print(f"Kształt macierzy cech: {X.shape}")
# Oczekiwany kształt: (Liczba_obrazów, 768) - bo GPT-2/ViT base ma zazwyczaj hidden size 768

# 4. Redukcja wymiarowości (t-SNE)
print("Obliczanie t-SNE...")
n_components = 2
perplexity = min(30, len(embeddings) - 1)
tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=42, init='pca', learning_rate='auto')
X_embedded = tsne.fit_transform(X)

# 5. Wizualizacja
plt.figure(figsize=(10, 8))
# Rysujemy punkty
plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c='purple', alpha=0.7, s=60, edgecolors='k')

plt.title(f"Przestrzeń cech z ViT (Encoder z modelu ViT-GPT2)\nDla {len(valid_files)} obrazów")
plt.xlabel("Wymiar 1")
plt.ylabel("Wymiar 2")
plt.grid(True, linestyle='--', alpha=0.3)

plt.show()