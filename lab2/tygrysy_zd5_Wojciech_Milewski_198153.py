import random
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches
import matplotlib.path as mpath
from matplotlib.animation import FuncAnimation
from PIL import Image
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class Wierzcholek:
    def __init__(self, x,y, id_tygrysa):
        self.x = x
        self.y = y
        self.id_tygrysa = id_tygrysa
    def __eq__(self, other):
        return abs(self.x-other.x) < 1e-10 and abs(self.y-other.y) < 1e-10
    def __repr__(self):
        return f"Punkt({self.x}, {self.y})"

class Point:
    def __init__(self,id, x, y, a=None):
        self.id = id
        self.x = x
        self.y = y
        self.alpha = random.uniform(0, 2 * math.pi)

        if a is None:
            self.a = random.uniform(4, 6)
        else:
            self.a= a
        self.beta=math.radians(random.uniform(0.5, 30))
        self.gamma=math.radians(random.uniform(0.5, 60))
        self.vx = self.a * 0.3 * math.cos(self.alpha)
        self.vy = self.a * 0.3 * math.sin(self.alpha)

    def odbicie_od_granic(self):

        kolejny_x= self.x+self.vx
        kolejny_y= self.y+self.vy

        hit=False

        if kolejny_x<0 or kolejny_x>100:
            self.vx = -self.vx
            hit=True
        if kolejny_y<0 or kolejny_y>100:
            self.vy = -self.vy
            hit=True

        if hit:
            v_total = math.sqrt(self.vx**2 + self.vy**2)
            if v_total>0:
                val = max(-1.0,min(1.0,self.vx/v_total))
                self.alpha = math.acos(val)
                if self.vy <0:
                    self.alpha = 2 * math.pi - self.alpha
        return hit

    def odbicie_od_plotu(self,sciany):
        for (p1, p2) in sciany:
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            dlugosc_sciany=dx*dx+dy*dy

            if dlugosc_sciany == 0: continue

            t= ((self.x-p1.x)*dx + (self.y-p1.y)*dy) / dlugosc_sciany
            t= max(0,min(1,t))

            najblizszy_x = p1.x +t*dx
            najblizszy_y = p1.y +t*dy

            dist_x = self.x - najblizszy_x
            dist_y = self.y - najblizszy_y
            odleglosc = math.sqrt(dist_x**2 + dist_y**2)

            if odleglosc < 2.0:
                if random.randint(1,10)==1:
                    return
                nx=-dy
                ny=dx
                d_n=math.sqrt(nx**2 + ny**2)
                nx/=d_n
                ny/=d_n

                if self.vx*nx+self.vy*ny < 0:
                    dot = self.vx*nx+self.vy*ny
                    self.vx = self.vx - 2*dot*nx
                    self.vy = self.vy - 2*dot*ny

                    v_total = math.sqrt(self.vx**2 + self.vy**2)
                    if v_total>0:
                        cos_val = max(-1.0,min(1.0,self.vx/v_total))

                        self.alpha = math.acos(cos_val)

                        if self.vy <0:
                            self.alpha = 2 * math.pi - self.alpha
                    return

    def move(self,sciezki_przeszkod):
        next_x = self.x + self.vx
        next_y = self.y + self.vy

        kolizja= False

        for path in sciezki_przeszkod:
            if path.contains_point((next_x, next_y)):
                kolizja = True
                break
        if kolizja:
            self.vx = -self.vx
            self.vy = -self.vy

            v_total = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if v_total > 0:
                val = max(-1.0, min(1.0, self.vx / v_total))
                self.alpha = math.acos(val)
                if self.vy < 0:
                    self.alpha = 2 * math.pi - self.alpha
        else:
            self.x = next_x
            self.y = next_y

    def __repr__(self):
        return f'Point({self.x}, {self.y})'

nazwa_pliku="tiger.gif"
skala=0.03
liczba_przeszkod=4

def generuj_szeciakat(cx,cy,bok):
    punkty=[]
    for i in range(6):
        kat = math.radians(60*i)
        px = cx+bok*math.cos(kat)
        py = cy+bok*math.sin(kat)
        punkty.append((px,py))
    return punkty

def przeszkody():
    wierzcholki=[]
    polaczenia = []

    for _ in range(liczba_przeszkod):
        cx = random.uniform(15,85)
        cy = random.uniform(15,85)
        bok = random.uniform(4,7)

        punkty_szesciokata = generuj_szeciakat(cx,cy,bok)
        wierzcholki.append(punkty_szesciokata)

        polaczenia.append(mpath.Path(punkty_szesciokata))
    return wierzcholki,polaczenia

wierzcholki_przeszkod, polaczenia_wierzcholkow_przeszkod = przeszkody()

def czy_w_przeszkodzie(x,y):
    for b in polaczenia_wierzcholkow_przeszkod:
        if b.contains_point((x,y)):
            return True
    return False

num_of_points=20
Points=[]

i=0
while i<num_of_points:
    px = random.uniform(5,95)
    py = random.uniform(5,95)

    if czy_w_przeszkodzie(px,py):
        continue
    point = Point(i,px,py)
    Points.append(point)
    i+=1

def cross_product(o, a, b):
    return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)


def calculate_hull(pts):
    n = len(pts)
    if n < 3: return pts

    start_point = pts[0]
    for p in pts:
        if p.y < start_point.y:
            start_point = p
        elif p.y == start_point.y and p.x < start_point.x:
            start_point = p

    hull = []
    current = start_point

    while True:
        hull.append(current)
        next_candidate = pts[0]

        for i in range(1, n):
            checking = pts[i]
            if checking == current: continue

            cp = cross_product(current, next_candidate, checking)
            dist_next = (next_candidate.x - current.x) ** 2 + (next_candidate.y - current.y) ** 2
            dist_check = (checking.x - current.x) ** 2 + (checking.y - current.y) ** 2

            if next_candidate == current or cp < 0 or (cp == 0 and dist_check > dist_next):
                next_candidate = checking

        current = next_candidate
        if current == start_point:
            break

    return hull
def triangle_points(p):
    kat_srodek = math.pi - p.beta - p.gamma
    bot = math.sin(p.gamma) / math.sin(kat_srodek) * p.a
    top = math.sin(p.beta) / math.sin(kat_srodek) * p.a

    p_0 = [p.x, p.y]

    x_top_r = p.x + top *math.cos(p.alpha+p.beta)
    y_top_r = p.y + top * math.sin(p.alpha+p.beta)
    p_top_r = [x_top_r, y_top_r]

    x_bot_r = p.x + bot * math.cos(p.alpha+(math.pi - p.gamma))
    y_bot_r = p.y + bot * math.sin(p.alpha+(math.pi - p.gamma))
    p_bot_r = [x_bot_r, y_bot_r]

    x_top_l = p.x + top * math.cos(p.alpha - p.beta)
    y_top_l = p.y + top * math.sin(p.alpha - p.beta)
    p_top_l = [x_top_l, y_top_l]

    x_bot_l = p.x + bot * math.cos(p.alpha -(math.pi - p.gamma))
    y_bot_l = p.y + bot * math.sin(p.alpha -(math.pi - p.gamma))
    p_bot_l = [x_bot_l, y_bot_l]
    return (p_0,p_top_r,p_bot_r), (p_0,p_top_l,p_bot_l)

def laczenie_tygrysow(tygrysy):

    do_usuniecia = []

    for i in range (len(tygrysy)):
        t1=tygrysy[i]

        if t1 in do_usuniecia:
            continue

        r1,l1 = triangle_points(t1)

        punkty=[r1[0],r1[1],r1[2],l1[0],l1[1],l1[2]]
        sciezka_t1 = mpath.Path(punkty)

        for j in range(len(tygrysy)):
            if i==j: continue
            t2 = tygrysy[j]
            if t2 in do_usuniecia: continue

            if sciezka_t1.contains_point((t2.x,t2.y)):
                nowe_a=math.sqrt(t1.a**2+t2.a**2)
                t1.a = nowe_a

                do_usuniecia.append(t2)
    for t in do_usuniecia:
        if t in tygrysy:
            tygrysy.remove(t)

fig, ax = plt.subplots()

def znajdz_tygrysa_po_id(tygrysy, id):
    for i in tygrysy:
        if i.id == id:
            return i
    return None

def znajdz_najblizszy_punkt(punkt_odniesienia,hull):
    if not hull: return None
    najblizszy = hull[0]
    min_dist = float('inf')
    for p in hull:
        dist = (p.x-punkt_odniesienia.x)**2 + (p.y-punkt_odniesienia.y)**2
        if dist < min_dist:
            min_dist = dist
            najblizszy = p
    return najblizszy

def klatki_gifa(nazwa_pliku):
    klatki = []
    try:
        gif = Image.open(nazwa_pliku)
        while True:
            klatka = gif.convert('RGBA')
            klatki.append(np.array(klatka))
            gif.seek(gif.tell()+1)
    except EOFError:
        pass
    except FileNotFoundError:
        print("Nie znaleziono pliku")
        dummy = np.zeros((20, 20, 4), dtype=np.uint8)
        dummy[:] = [255,0,0,255]
        klatki.append(dummy)
    return klatki

klatki_tygrysa = klatki_gifa(nazwa_pliku)



def animacja(klatki):
    ax.clear()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_title('Tygrysy')

    if not hasattr(animacja, "sciany"):
        animacja.sciany=[]
        animacja.ostatni_punkt = None
        animacja.dlugosc_rysowania = 0.0
        animacja.cel_segmentu = None
        animacja.koniec = False
        animacja.miejsce_zjedzenia = None

    for p in Points:
        p.move(polaczenia_wierzcholkow_przeszkod)
        p.odbicie_od_granic()
        p.odbicie_od_plotu(animacja.sciany)

    laczenie_tygrysow(Points)
    wszystkie_punkty = []

    for p in Points:
        r, l = triangle_points(p)
        skrzydlo = r + l
        for wsp in skrzydlo:
            w = Wierzcholek(wsp[0], wsp[1],p.id)
            wszystkie_punkty.append(w)

    hull=[]

    if len(wszystkie_punkty) >= 3:
        hull = calculate_hull(wszystkie_punkty)

        if animacja.ostatni_punkt is None and len(hull) > 0:
            animacja.ostatni_punkt = hull[0]
    #Rysowanie rzeczy
    for w in wierzcholki_przeszkod:
        polygon= patches.Polygon(w, closed=True,edgecolor='black')
        ax.add_patch(polygon)

    obecny_obrazek=None
    if klatki_tygrysa:
        indeks_klatki = klatki % len(klatki_tygrysa)
        obecny_obrazek = klatki_tygrysa[indeks_klatki]

    for p in Points:
        if obecny_obrazek is not None:
            zoom = p.a * skala
            imagebox = OffsetImage(obecny_obrazek, zoom=zoom)
            ab = AnnotationBbox(imagebox, (p.x, p.y), frameon=False)
            ax.add_artist(ab)

    for p1,p2 in animacja.sciany:
        ax.plot([p1.x,p2.x], [p1.y,p2.y], 'g-')

    if len(hull) >=3 and not animacja.koniec:

        if animacja.cel_segmentu is None:
            cel_znaleziony = False

            if len(animacja.sciany) > 2:
                poczatek_sciany = animacja.sciany[0][0]
                obecna_pozycja = animacja.ostatni_punkt
                dystans_od_poczatku = math.sqrt((obecna_pozycja.x - poczatek_sciany.x)**2 + (obecna_pozycja.y - poczatek_sciany.y)**2)

                if dystans_od_poczatku < 25.0:
                    animacja.cel_segmentu = poczatek_sciany
                    cel_znaleziony = True

            if not cel_znaleziony:
                start_ref = znajdz_najblizszy_punkt(animacja.ostatni_punkt,hull)
                if start_ref:
                    try:
                        id = hull.index(start_ref)
                        id_next = (id+1)%len(hull)
                        animacja.cel_segmentu = hull[id_next]
                    except ValueError:
                        animacja.cel_segmentu = hull[0]
        if animacja.cel_segmentu:
            try:
                tygrys_start= znajdz_tygrysa_po_id(Points, animacja.ostatni_punkt.id_tygrysa)
                krok = 2* tygrys_start.a if tygrys_start else 10.0
            except:
                krok = 10

            cel_x,cel_y = animacja.cel_segmentu.x, animacja.cel_segmentu.y
            start_x, start_y = animacja.ostatni_punkt.x, animacja.ostatni_punkt.y

            odleglosc_od_celu = math.sqrt((-start_x+cel_x)**2 + (-start_y+cel_y)**2)
            animacja.dlugosc_rysowania +=krok
            if animacja.dlugosc_rysowania >= odleglosc_od_celu:

                if len(animacja.sciany) > 2 and animacja.cel_segmentu == animacja.sciany[0][0]:
                     nowy_punkt_staly = animacja.sciany[0][0]
                     animacja.koniec = True
                else:

                    nowy_punkt_staly = Wierzcholek(cel_x,cel_y,getattr(animacja.cel_segmentu,'id_tygrysa',-1))

                animacja.sciany.append((animacja.ostatni_punkt, nowy_punkt_staly))
                animacja.ostatni_punkt = nowy_punkt_staly
                animacja.dlugosc_rysowania = 0
                animacja.cel_segmentu = None
            else:
                if odleglosc_od_celu >0:
                    stosunek = animacja.dlugosc_rysowania/odleglosc_od_celu
                    curr_x= start_x + (cel_x - start_x)*stosunek
                    curr_y= start_y + (cel_y - start_y)*stosunek
                    ax.plot([start_x,curr_x], [start_y,curr_y], 'g-')
                    ax.scatter(curr_x,curr_y, color='lime')
                    for tygrys in Points:
                        t_r,t_l = triangle_points(tygrys)

                        sciezka_r = mpath.Path(t_r)
                        sciezka_l = mpath.Path(t_l)

                        if sciezka_r.contains_point((curr_x,curr_y)) or sciezka_l.contains_point((curr_x,curr_y)):
                            animacja.koniec = True
                            animacja.miejsce_zjedzenia = (curr_x,curr_y)
                            break
    if animacja.miejsce_zjedzenia is not None:
        x,y = animacja.miejsce_zjedzenia
        ax.text(x, y, "Zjedzony", color='red', fontsize=8, fontweight='bold')
ani = FuncAnimation(fig, animacja, frames=200, interval=50)

plt.show()