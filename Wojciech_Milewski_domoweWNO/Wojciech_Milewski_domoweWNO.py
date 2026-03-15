import cv2
import numpy as np

template = "template.png"
ilosc_plikow=6
#______________________________
#Zdjecia przeklikuje się spacją
#______________________________

def range_bez_cv(img,kolor):

    maska = (img[:,:,0]==kolor[0] ) & (img[:,:,1]==kolor[1] ) & (img[:,:,2]==kolor[2])

    return maska.astype(np.uint8)*255 #daje bialy gdzie kolor pasuje

def mapa_gestosci(maska,w_temp,h_temp):

    h_img, w_img = maska.shape

    calka = maska.astype(np.float32).cumsum(axis=0).cumsum(axis=1)

    macierz_calkowa = np.pad(calka,((1,0),(1,0)),mode='constant',constant_values=0)

    A= macierz_calkowa[:-h_temp,:-w_temp]
    B= macierz_calkowa[:-h_temp,w_temp:]
    C= macierz_calkowa[h_temp:,:-w_temp]
    D= macierz_calkowa[h_temp:,w_temp:]
    wynik = (D-B-C+A)

    mapa_wynik = np.zeros((h_img,w_img),dtype=np.float32)
    wynik_h,wynik_w = wynik.shape
    mapa_wynik[:wynik_h,:wynik_w]= wynik

    return mapa_wynik

def dylatacja(maska,liczba_iteracji=1):

    wynik = maska.copy()

    for _ in range(liczba_iteracji):
        M=wynik

        up = np.pad(M[1:,:],((0,1),(0,0)))
        down = np.pad(M[:-1,:],((1,0),(0,0)))
        left = np.pad(M[:,1:],((0,0),(0,1)))
        right = np.pad(M[:,:-1],((0,0),(1,0)))
        wynik = wynik|up|down|left|right
    return wynik

def flooding(maska):

    height,width = maska.shape
    odwiedzone = np.zeros_like(maska,dtype=bool)
    znalezione_ramki=[]

    punkty_y,punkty_x =np.where(maska>0)
    stos= np.column_stack((punkty_y,punkty_x))

    for py,px in stos:
        if odwiedzone[py,px]:
            continue

        stos = [(py,px)]
        odwiedzone[py,px] = True

        min_x,max_x=px,px
        min_y,max_y=py,py

        while stos:
            aktualny_y,aktualny_x=stos.pop()
            if aktualny_x <min_x:
                min_x=aktualny_x
            if aktualny_x > max_x:
                max_x=aktualny_x
            if aktualny_y <min_y:
                min_y=aktualny_y
            if aktualny_y > max_y:
                max_y=aktualny_y

            neighbors = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]

            for dx,dy in neighbors:
                nowy_y,nowy_x=aktualny_y+dy,aktualny_x+dx

                if 0<=nowy_x<width and 0<=nowy_y<height:
                    if maska[nowy_y,nowy_x]>0 and not odwiedzone[nowy_y,nowy_x]:
                        odwiedzone[nowy_y,nowy_x] = True
                        stos.append((nowy_y,nowy_x))
        w_ramki = max_x-min_x+1
        h_ramki = max_y-min_y+1
        if w_ramki>2 and h_ramki>2:
            znalezione_ramki.append((min_x,min_y,w_ramki,h_ramki))
    return znalezione_ramki

def kwantyzacja(img,dzielnik):
    return (img//dzielnik)*dzielnik

def prep_template(sciezka_temp):
    temp= cv2.imread(sciezka_temp,cv2.IMREAD_UNCHANGED)
    if temp is None:
        return None

    h_temp,w_temp= temp.shape[:2]

    temp_bgr=temp[:,:,:3]
    temp_alpha=temp[:,:,3]

    nie_przezroczyste = kwantyzacja(temp_bgr,12)[temp_alpha>0]#jak bardzo podzielone kolory

    kolory,liczniki = np.unique(nie_przezroczyste,axis=0,return_counts=True)
    indeksy = np.argsort(liczniki)[::-1]
    main_kolory = kolory[indeksy][:20]
    area = h_temp*w_temp

    return main_kolory,h_temp,w_temp,area

def przetwarzanie_pliku(sciezka_pliku,dane_wzorca):
    obraz=cv2.imread(sciezka_pliku)
    if obraz is None:
        return True
    main_kolory, h_temp, w_temp, area = dane_wzorca
    obraz_kwant=kwantyzacja(obraz,12)
    h_obraz,w_obraz= obraz.shape[:2]

    ilosc_kolorow_temp=len(main_kolory)
    sample= obraz_kwant[::10,::10].reshape(-1,3)
    ilosc_kolorow_obraz=len(np.unique(sample,axis=0))

    prog = min(15,ilosc_kolorow_temp)#prog ilosci kolorow na template

    min_gestosc = float(area)*0.05

    maska_pikseli=np.zeros((h_obraz,w_obraz),dtype=np.uint8)
    mapa_roznosci_kolorow= np.zeros((h_obraz,w_obraz),dtype=np.float32)
    mapka_gestosci=np.zeros((h_obraz,w_obraz),dtype=np.float32)

    for kolor in main_kolory:
        maska_koloru= range_bez_cv(obraz_kwant,kolor)#maska wystapien tego koloru
        maska_koloru_logiczna = (maska_koloru>0).astype(np.float32)
        maska_pikseli = maska_pikseli | maska_koloru

        gestosc_koloru = mapa_gestosci(maska_koloru_logiczna,w_temp,h_temp)#ilosc wystapien koloru w ramkach template
        mapka_gestosci += gestosc_koloru

        wystapienie_koloru = (gestosc_koloru>1).astype(np.float32)
        mapa_roznosci_kolorow +=wystapienie_koloru

    maska_both = (mapa_roznosci_kolorow >= prog)&(mapka_gestosci >= min_gestosc)
    maska_final = maska_both.astype(np.uint8) * 255

    obiekty = flooding(maska_final)

    wynik = obraz.copy()
    znalezione=0
    for (x_ramki,y_ramki,w_ramki,h_ramki) in obiekty:
        mid_x = x_ramki + w_ramki // 2
        mid_y = y_ramki + h_ramki // 2

        margin_w=int(w_temp*0.6)
        margin_h=int(h_temp*0.6)

        roi_x1 = max(0,mid_x - w_temp//2-margin_w)
        roi_y1 = max(0,mid_y - h_temp//2-margin_h)
        roi_x2 = min(w_obraz,mid_x + w_temp//2+margin_w)
        roi_y2 = min(h_obraz,mid_y + h_temp//2+margin_h)

        wycinek= maska_pikseli[roi_y1:roi_y2,roi_x1:roi_x2]

        if wycinek.size==0:
            continue
        closed_wycinek= dylatacja(wycinek,liczba_iteracji=2)
        obiekty_roi=flooding(closed_wycinek)#by ramka była dokładniejsza

        if obiekty_roi:
            ramki=np.array(obiekty_roi)
            pola = ramki[:,2]*ramki[:,3]
            kx,ky,kw,kh=ramki[np.argmax(pola)]
            final_x = roi_x1 + kx
            final_y = roi_y1 + ky
            cv2.rectangle(wynik,(final_x,final_y),(final_x+kw,final_y+kh),(0,255,0),3)
            znalezione+=1
        else:
            sx=max(0,mid_x)
            sy=max(0,mid_y)
            cv2.rectangle(wynik,(sx,sy),(sx+w_temp,sy+h_temp),(0,0,255),2)
    if h_obraz>800:
        skala=800/h_obraz
        cv2.imshow("Wynik",cv2.resize(wynik,(int(w_obraz*skala),int(h_obraz*skala))))
    else:
        cv2.imshow("Wynik",wynik)
    k=cv2.waitKey(0)
    return True

def main():
    dane=prep_template(template)
    if not dane:
        print("Nie znaleziono template")
        return
    for i in range(1,ilosc_plikow+1):
        nazwa_pliku=f"{i}.jpg"
        if not przetwarzanie_pliku(nazwa_pliku,dane):
            break

    cv2.destroyAllWindows()
if __name__=="__main__":
    main()




