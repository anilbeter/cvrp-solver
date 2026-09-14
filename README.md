# CVRP Solver

Kapasiteli araç rotalama problemini (CVRP) Google OR-Tools ile çözdüğüm bir
proje. Çözücüyü optimumu bilinen bir benchmark örneğinde test ettim, sonra araç
sayısı, kapasite ve süre limitinin sonucu nasıl etkilediğine baktım.

## Problem

Bir depo ve n müşteri var, her müşterinin belli bir talebi var. Aynı
kapasitedeki K araç depodan çıkıp müşterileri dolaşıyor ve depoya geri dönüyor.

- Her müşteriye tam bir kez gidilmeli
- Hiçbir araç kapasitesinden fazla yük taşıyamaz
- Amaç toplam mesafeyi en aza indirmek

## Veri

Augerat et al. (1995) Set A'dan **A-n32-k5** örneğini kullandım.

| Özellik             | Değer                                  |
| ------------------- | -------------------------------------- |
| Düğüm sayısı        | 32 (1 depo + 31 müşteri)               |
| Araç kapasitesi     | 100                                    |
| Toplam talep        | 410                                    |
| Minimum araç sayısı | 5                                      |
| Sıkılık (410 / 500) | 0.82                                   |
| Mesafe              | Öklid, tam sayıya yuvarlanmış (EUC_2D) |
| Bilinen optimum     | 784                                    |

Toplam talep 410 ve her araç en fazla 100 taşıyabildiği için en az 5 araç
gerekiyor. 5 araçla ortalama doluluk %82 oluyor, yani kapasite kısıtı oldukça
sıkı.

## Sonuç

5 araç ve 30 saniyelik süre limitiyle çözücü 784'ü buldu:

- Toplam mesafe: **784** (bilinen optimum 784, fark %0.00)
- Kullanılan araç: 5 / 5
- En dolu araç: 98 / 100

784'ün optimal olduğu literatürde kanıtlanmış, dolayısıyla bulunan çözüm de
optimal.

![Rotalar](results/routes_base.png)

## Duyarlılık analizi

Her denemede tek bir parametreyi değiştirip diğerlerini sabit tuttum (kapasite
100, 5 araç, 30 sn).

### Kapasite

| Kapasite | Mesafe | 100'e göre azalma | Kullanılan araç | Min. araç | Maks. yük |
| -------- | ------ | ----------------- | --------------- | --------- | --------- |
| 100      | 784    | -                 | 5               | 5         | 98        |
| 120      | 719    | %8.29             | 4               | 4         | 115       |
| 140      | 645    | %17.73            | 3               | 3         | 138       |
| 160      | 629    | %19.77            | 3               | 3         | 158       |
| 200      | 562    | %28.32            | 3               | 3         | 195       |

![Kapasite](results/sweep_capacity.png)

Min. araç, talebi taşımak için gereken en az araç sayısı (410 / kapasite,
yukarı yuvarlanmış). 784 sadece kapasite 100 için geçerli, kapasite değişince
ortada farklı bir problem oluyor. Bu yüzden tabloya optimuma fark yerine
kapasite 100'e göre azalmayı yazdım. Diğer kapasitelerin bilinen bir optimumu
yok, buradaki değerler çözücünün 30 saniyede bulabildiği en iyi çözümler.

Mesafedeki büyük düşüşler araç sayısının azaldığı adımlarda geliyor. Kapasite
100'den 140'a çıkınca araç sayısı 5'ten 3'e iniyor ve mesafe %17.7 kısalıyor.
Çözücü her kapasitede tam minimum sayıda araç kullanıyor.

140'tan sonra araç sayısı 3'te sabit kalıyor (200 kapasiteyle bile 2 araç
yetmiyor, 2 x 200 = 400) ama mesafe düşmeye devam ediyor: 645'ten 562'ye, %12.9
daha. Kapasite gevşeyince müşteriler daha mantıklı gruplanabiliyor. Düşüş
düzenli de değil. Kapasitedeki her 1 birimlik artış mesafeyi 140-160 arasında
ortalama 0.8, 160-200 arasında ise 1.7 azaltıyor. İlk bakışta azalan getiri
bekliyordum ama veri öyle demiyor.

### Araç sayısı

| Araç | Mesafe    | Kullanılan araç |
| ---- | --------- | --------------- |
| 4    | çözüm yok | -               |
| 5    | 784       | 5               |
| 6    | 784       | 5               |
| 7    | 784       | 5               |
| 8    | 784       | 5               |

![Araç sayısı](results/sweep_vehicles.png)

4 araçla çözüm yok, çünkü 4 x 100 = 400 ve toplam talep 410. 5'ten fazla araç
verince fazlası hiç kullanılmıyor. Her ek araç depoya bir gidiş-dönüş daha
demek, o yüzden çözücü onları boş bırakıyor.

Fazla araç sonucu değiştirmiyor ama aramayı yavaşlatıyor. 5 araçla optimuma 7
saniye civarında ulaşılıyor, 8 araçla 20 saniye civarında. Boş araçlar arama
uzayını büyütüyor. Başta süre limitini 10 saniye tutmuştum ve 8 araçlı model
796'da kalıyordu, limiti bu yüzden 30 saniyeye çıkardım.

### Süre limiti

| Süre (sn) | Mesafe | Optimuma fark |
| --------- | ------ | ------------- |
| 1         | 796    | %1.53         |
| 5         | 796    | %1.53         |
| 10        | 784    | %0.00         |
| 30        | 784    | %0.00         |
| 60        | 784    | %0.00         |

![Süre](results/sweep_time.png)

Çözücü 796'yı daha ilk saniyede buluyor ve birkaç saniye orada takılı kalıyor.
Guided Local Search'ün ceza mekanizması sonunda aramayı oradan çıkarıyor ve
784'e yaklaşık 7. saniyede ulaşıyor. Bunu her iyileşmenin zamanını solution
callback ile kaydederek ölçtüm.

Süre limiti gerçek saate göre işlediği için 10 saniye bu eşiğe çok yakın. Aynı
ayar bir çalıştırmada 796 verdi, daha yavaş bir makinede de farklı sonuç
çıkabilir.

Şunu da not edeyim: metasezgisel bir yöntem optimumu bulsa bile optimum
olduğunu kanıtlayamaz. 784'ün optimal olduğunu literatürden biliyoruz. Kanıt
gerekiyorsa CP-SAT veya MIP gibi tam bir yöntem lazım. Problem büyüdükçe de süre
limiti çok daha önemli hale geliyor.

## Yöntem

Çözüm iki adımdan oluşuyor:

1. `PATH_CHEAPEST_ARC` ile başlangıç çözümü: her adımda en yakın uygun müşteri
   eklenerek açgözlü bir rota kuruluyor.
2. `GUIDED_LOCAL_SEARCH` ile iyileştirme: başlangıç çözümü süre limiti dolana
   kadar yerel aramayla iyileştiriliyor. Arama bir yerel optimuma takılınca sık
   kullanılan arklar cezalandırılıyor ve arama başka bölgelere kayıyor. Bu
   yüzden süre bitmeden durmuyor.

Kapasite kısıtını OR-Tools'un dimension yapısıyla kurdum. Rota boyunca biriken
yük takip ediliyor ve araç kapasitesiyle sınırlanıyor.

**Alt-tur eliminasyonu.** Ark tabanlı bir MIP modelinde derece kısıtları tek
başına depoya bağlı olmayan kapalı döngüleri engellemiyor, o yüzden MTZ ya da
kapasite kesmeleri gibi ek kısıtlar gerekiyor. OR-Tools'ta buna gerek yok.
Rotalama modelinde her düğümün bir "sonraki düğüm" (`NextVar`) değişkeni var ve
motor, her aracın başlangıçtan bitişe döngüsüz bir yol izlemesini kendisi
sağlıyor.

**Mesafe hesabı.** Burada başta yanıldım. TSPLIB'in `EUC_2D` tanımında her
mesafe en yakın tam sayıya yuvarlanıyor ve 784 de bu kuralla hesaplanmış. İlk
versiyonda mesafeleri yuvarlamadan kullanmıştım, çözücü 787.08 bulmuştu ve
optimumdan %0.39 uzakta olduğumu düşünmüştüm. Aslında iki farklı problemi
karşılaştırıyormuşum. 784 maliyetli optimal rotaların yuvarlanmamış gerçek
uzunluğu 787.81, yani yuvarlamasız çözüm gerçek mesafede optimal rotalardan bile
kısaydı. İki kural farklı optimal rotalara götürüyor. Karşılaştırmak isterseniz
`build_distance_matrix(coords, rounded=False)` ile yuvarlamayı kapatabilirsiniz.

**Ölçekleme.** OR-Tools rotalama motoru sadece tam sayı maliyetlerle çalışıyor.
Çözücü mesafeleri 1000 ile çarpıp yuvarlıyor, raporlarken tekrar bölüyor.
Böylece yuvarlama kapalıyken de üç ondalık basamak korunuyor.

## Kurulum

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Süre limitleri yüzünden tüm deneylerin bitmesi 7 dakika kadar sürüyor. Çıktılar
`results/` klasörüne yazılıyor.

## Dosyalar

- `data/A-n32-k5.vrp`: benchmark örneği (TSPLIB formatı)
- `src/parser.py`: .vrp dosyasını okuma ve mesafe matrisi
- `src/solver.py`: OR-Tools modeli
- `src/plot.py`: rota haritası
- `src/sensitivity.py`: parametre taramaları, tablolar, CSV ve grafikler
- `main.py`: bütün deneyleri çalıştırır
