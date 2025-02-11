# HungarianMosaicBuilder
Ce projet permet de générer une mosaïque à partir d’une image principale et d’une banque d’images. L'algorithme divise l'image principale en petites sections et sélectionne les meilleures correspondances dans la banque d'images en fonction de la similarité colorimétrique.

<p align="center">
    <img src="starwars3.jpg" width="150"> 
    <img src="image.png" width="150">
</p>

## Librairies utilisées
- `glob` : Parcours des fichiers de la banque d’images.
- `PIL (Pillow)` : Manipulation et traitement des images.
- `numpy` : Calculs de moyenne RGB et manipulation matricielle.
- `spatial` : (Optionnel) Recherche rapide des correspondances via `spatial.KDTree`.

### Dépendances 
```bash
pip install pillow numpy scipy
```

## Fonctionnement

### Récupération de la banque d’images
- Lecture et redimensionnement des tuiles (petites images).
- Calcul de la moyenne RGB de chaque tuile via `numpy`.

### Génération de la mosaïque
- Redimension de l’image principale aux dimensions multiples de la taille des tuiles.
- Assemblage en recollant chaque tuile à la position adéquate.
- Réutilisation de tuiles si nécessaire pour couvrir l’intégralité de l’image principale.

### Redimensionner l’image principale
L’image principale est adaptée aux dimensions des tuiles pour éviter les décalages et erreurs d’alignement.

### Taille des tuiles (`img_size`)
Ajuster la taille des tuiles (`50x50` par défaut) pour influencer la granularité de la mosaïque.

### Nombre de tuiles
Une limite peut être appliquée sur la quantité d’images chargées (ex. 600 max). Modifiable selon les besoins.

### Banque d'images
- Banque d’images dans `splash/` (ou modifier la variable `banque_path`).
- Image principale (ex. `starwars3.jpg`) dans le même dossier que le script.

Le fichier `munkres.jpg` sera généré avec la mosaïque finale.



