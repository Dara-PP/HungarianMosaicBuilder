import glob
import os
import sys
import random
import numpy as np
from PIL import Image  # pour lire et écrire des images
from math import ceil

# Afficher toute la matrice
np.set_printoptions(threshold=sys.maxsize)

def min_zero_row(zero_mat, mark_zero):
    """
    Sélectionne la ligne avec le moins de zéros dans zero_mat,
    marque un zéro, puis invalide la ligne et la colonne associées.
    """
    min_row = [99999, -1]
    # Trouver la ligne avec le moins de zéros encore disponibles
    for row_num in range(zero_mat.shape[0]):
        nb_true = np.sum(zero_mat[row_num] == True)
        if nb_true > 0 and min_row[0] > nb_true:
            min_row = [nb_true, row_num]

    # Marquer le premier zéro trouvé dans cette ligne
    zero_index = np.where(zero_mat[min_row[1]] == True)[0][0]
    mark_zero.append((min_row[1], zero_index))

    # Invalider la ligne et la colonne correspondantes
    zero_mat[min_row[1], :] = False
    zero_mat[:, zero_index] = False


def mark_matrix(mat):
    """
    Identifie un ensemble de lignes et de colonnes pour couvrir tous les zéros de la matrice.
    Retourne les positions marquées et les lignes/colonnes utilisées pour ajuster la matrice.
    """
    cur_mat = mat
    zero_bool_mat = (cur_mat == 0)
    zero_bool_mat_copy = zero_bool_mat.copy()

    marked_zero = []
    # Tant qu'il y a des True (= zéros) disponibles, on marque
    while True in zero_bool_mat_copy:
        min_zero_row(zero_bool_mat_copy, marked_zero)

    # Séparation des indices de lignes et colonnes marqués
    marked_zero_row = [t[0] for t in marked_zero]
    marked_zero_col = [t[1] for t in marked_zero]

    # Étape 2-2-1
    non_marked_row = list(set(range(cur_mat.shape[0])) - set(marked_zero_row))

    marked_cols = []
    check_switch = True
    while check_switch:
        check_switch = False
        # Étape 2-2-2 : on regarde les zéros pour chaque ligne non marquée
        for row_index in non_marked_row:
            row_array = zero_bool_mat[row_index, :]
            for col_index in range(row_array.shape[0]):
                if row_array[col_index] and col_index not in marked_cols:
                    # Étape 2-2-3
                    marked_cols.append(col_index)
                    check_switch = True

        # Étape 2-2-4 : si une case marquée est dans une colonne marquée, on ajoute sa ligne à non_marked_row
        for row_num, col_num in marked_zero:
            if row_num not in non_marked_row and col_num in marked_cols:
                non_marked_row.append(row_num)
                check_switch = True

    # Lignes marquées = toutes celles non dans non_marked_row
    marked_rows = list(set(range(mat.shape[0])) - set(non_marked_row))
    return marked_zero, marked_rows, marked_cols


def adjust_matrix(mat, cover_rows, cover_cols):
    """
    Ajuste la matrice en soustrayant le minimum des éléments non couverts et
    en l'ajoutant aux intersections couvertes pour créer plus de zéros.
    """
    cur_mat = mat
    non_zero_element = []

    # Récupère le minimum des éléments non couverts
    for row in range(len(cur_mat)):
        if row not in cover_rows:
            for col in range(len(cur_mat[row])):
                if col not in cover_cols:
                    non_zero_element.append(cur_mat[row][col])
    min_num = min(non_zero_element)

    # Soustraction du min aux éléments non couverts
    for row in range(len(cur_mat)):
        if row not in cover_rows:
            for col in range(len(cur_mat[row])):
                if col not in cover_cols:
                    cur_mat[row, col] -= min_num

    # Ajout du min aux intersections couvertes
    for row in cover_rows:
        for col in cover_cols:
            cur_mat[row, col] += min_num

    return cur_mat


def hungarian_algorithm(mat):
    """
    Implémentation de l'algorithme hongrois sur la matrice fournie.
    Retourne les positions (ligne, colonne) qui minimisent la somme.
    """
    dim = mat.shape[0]
    cur_mat = mat.copy()

    # Étape 1 : pour chaque colonne, on soustrait le minimum
    for col_num in range(cur_mat.shape[1]):
        cur_mat[:, col_num] -= np.min(cur_mat[:, col_num])

    zero_count = 0
    while zero_count < dim:
        # Étapes 2 & 3 : marquage et comptage du nb de lignes/colonnes nécessaires
        ans_pos, marked_rows, marked_cols = mark_matrix(cur_mat)
        zero_count = len(marked_rows) + len(marked_cols)

        # Étape 4 : s'il n'y a pas assez de lignes/colonnes pour couvrir tous les zéros, on ajuste
        if zero_count < dim:
            cur_mat = adjust_matrix(cur_mat, marked_rows, marked_cols)

    return ans_pos


def ans_calculation(mat, pos):
    """
    Calcule la somme des valeurs aux positions pos et construit une matrice
    avec uniquement ces positions renseignées.
    """
    total = 0
    ans_mat = np.zeros((mat.shape[0], mat.shape[1]))
    for (r, c) in pos:
        total += mat[r, c]
        ans_mat[r, c] = mat[r, c]
    return total, ans_mat


def main():
    banque_path = "splash\\*"
    img_size = (50, 50)

    # Récupération des fichiers
    banque_tiles = [file for file in glob.glob(banque_path)]

    # Limiter arbitrairement à 600 images pour l’exemple
    images = []
    m = 0
    for chm in banque_tiles:
        if m < 600:
            m += 1
            img = Image.open(chm)
            img = img.resize(img_size)
            images.append(img)

    # Calcul des couleurs moyennes de chaque image (RGB)
    colors = []
    for img in images:
        moy_color = np.array(img).mean(axis=0).mean(axis=0)
        colors.append(moy_color)

    # Lecture de l'image principale
    main_photo = Image.open("starwars3.jpg")
    width = int(np.round(main_photo.size[0] / img_size[0]))
    height = int(np.round(main_photo.size[1] / img_size[1]))
    resized_photo = main_photo.resize((width, height))

    # Préparation de la matrice de différence colorimétrique
    # et de la matrice d’affectation
    n = width * height
    matrix = np.zeros((m, m))
    l = 0

    for i in range(width):
        for j in range(height):
            pixel = resized_photo.getpixel((i, j))
            r1, g1, b1 = pixel
            for index, item in enumerate(colors):
                r2, g2, b2 = item
                ecart_color = ceil(abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2))
                matrix[l, index] = ecart_color
            l += 1

    # Pour remplir la matrice si on a plus de lignes (m) que de cases réelles (n)
    for i in range(m):
        for j in range(m):
            if i >= n:
                max_val = np.max(matrix)
                matrix[i, j] = max_val

    # Application de l’algorithme hongrois
    ans_pos = hungarian_algorithm(matrix)
    ans, ans_mat = ans_calculation(matrix, ans_pos)

    # Construction de l’image finale (mosaïque)
    output = Image.new('RGB', main_photo.size)
    closest_tiles = np.zeros((width, height), dtype=np.uint32)

    k = 0
    for i in range(width):
        for j in range(height):
            if k < n:
                # On récupère la colonne affectée pour la case k
                result = np.where(ans_mat[k] == np.max(ans_mat[k]))
                closest_tiles[i, j] = result[0][0]

            x, y = i * img_size[0], j * img_size[1]
            output.paste(images[closest_tiles[i, j]], (x, y))
            k += 1

            # Impression de l’indice i pour visualiser la progression
            print(i)

    # Sauvegarde du résultat
    output.save("munkres.jpg")

    """
    linear_sum_assignment :
    row_ind, col_ind = linear_sum_assignment(matrix)
    total_cost = matrix[row_ind, col_ind].sum()
    print(col_ind)
    print('Total cost:', total_cost)
    """


if __name__ == '__main__':
    main()
