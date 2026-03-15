import cv2
import numpy as np

def znajdz_obiekty_bbox(maska):
    h, w = maska.shape
    odwiedzone = np.zeros((h, w), dtype=bool)
    lista_boxow = []

    y_idxs, x_idxs = np.where(maska)
    punkty = list(zip(y_idxs, x_idxs))

    for y_start, x_start in punkty:
        if odwiedzone[y_start, x_start]: continue
        stos = [(y_start, x_start)]
        odwiedzone[y_start, x_start] = True
        xs, ys = [], []
        while stos:
            cy, cx = stos.pop()
            xs.append(cx)
            ys.append(cy)
            sasiedzi = [(cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)]
            for ny, nx in sasiedzi:
                if 0 <= ny < h and 0 <= nx < w:
                    if maska[ny, nx] and not odwiedzone[ny, nx]:
                        odwiedzone[ny, nx] = True
                        stos.append((ny, nx))
        if len(xs) > 50:
            x_min, x_max = min(xs), max(xs)
            y_min, y_max = min(ys), max(ys)
            lista_boxow.append((x_min, y_min, x_max, y_max))
    return lista_boxow



img_org = cv2.imread("org.jpg")
img_edited = cv2.imread("edited.jpg")

if img_edited is None or img_org is None:
    print("Brak plikow")
    exit()

roznica= np.abs(img_org.astype(np.int16) - img_edited.astype(np.int16))
roznica_total = np.sum(roznica,axis=2)
maska = roznica_total>40
bounding_boxy = znajdz_obiekty_bbox(maska)

img_z_ramkami= img_edited.copy()

h_orig, w_orig = img_z_ramkami.shape[:2]

obraz_koncowy_bgra = np.zeros((h_orig, w_orig, 4), dtype=np.uint8)

for i, (x1, y1, x2, y2) in enumerate(bounding_boxy):

    cv2.rectangle(img_z_ramkami, (x1, y1), (x2, y2), (0, 255, 0), 2)

    wycinek_bgr = img_z_ramkami[y1:y2 + 1, x1:x2 + 1]
    wycinek_maska = maska[y1:y2 + 1, x1:x2 + 1]

    kanal_alfa = (wycinek_maska * 255).astype(np.uint8)

    obraz_koncowy_bgra[y1:y2 + 1, x1:x2 + 1, 0:3] = wycinek_bgr
    obraz_koncowy_bgra[y1:y2 + 1, x1:x2 + 1, 3] = kanal_alfa

if len(bounding_boxy) > 0:
    cv2.imshow("Wynik", obraz_koncowy_bgra)
    cv2.imwrite("wynik.png", obraz_koncowy_bgra)

cv2.imshow("Oryginal", img_z_ramkami)
cv2.waitKey(0)