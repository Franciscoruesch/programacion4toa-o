import sys, random, pygame

# Configuración básica
COLS, ROWS, CELL = 10, 20, 30
ANCHO, ALTO = COLS * CELL + 150, ROWS * CELL
FPS = 60

# Las 7 piezas clásicas (I, O, T, J, L, S, Z) y sus colores
PIEZAS = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]
COLORES = [
    (0, 240, 240), (240, 240, 0), (160, 0, 240),
    (0, 100, 240), (240, 140, 0), (0, 240, 80), (240, 40, 40)
]

def rotar(forma):
    return [list(c) for c in zip(*forma[::-1])]

def colision(tablero, forma, px, py):
    for r, fila in enumerate(forma):
        for c, val in enumerate(fila):
            if val:
                x, y = px + c, py + r
                if x < 0 or x >= COLS or y >= ROWS:
                    return True
                if y >= 0 and tablero[y][x]:
                    return True
    return False

def nueva_pieza():
    idx = random.randrange(len(PIEZAS))
    forma = PIEZAS[idx]
    color = COLORES[idx]
    x = (COLS - len(forma[0])) // 2
    return forma, color, x, 0

def dibujar_bloque(pantalla, x, y, color):
    r = pygame.Rect(x, y, CELL, CELL)
    pygame.draw.rect(pantalla, color, r, border_radius=3)
    pygame.draw.rect(pantalla, (255, 255, 255), r, width=1, border_radius=3)

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 46, bold=True)

    tablero = [[None] * COLS for _ in range(ROWS)]
    pieza, color, px, py = nueva_pieza()
    sig_pieza, sig_color, _, _ = nueva_pieza()

    puntos, lineas = 0, 0
    tiempo_caida = 0
    pausa = False
    game_over = False

    while True:
        dt = reloj.tick(FPS)
        tiempo_caida += dt
        vel = max(100, 700 - (lineas // 5) * 60)

        titulo = f"Tetris | Puntos: {puntos} | Lineas: {lineas}"
        if pausa:
            titulo += " [PAUSA]"
        elif game_over:
            titulo += " [GAME OVER - Presiona ENTER o R]"
        pygame.display.set_caption(titulo)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                # Pausar y reanudar con SHIFT o ESC
                if evento.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_ESCAPE) and not game_over:
                    pausa = not pausa

                # Reiniciar partida con R o con ENTER tras game over
                if evento.key == pygame.K_r or (game_over and evento.key == pygame.K_RETURN):
                    tablero = [[None] * COLS for _ in range(ROWS)]
                    pieza, color, px, py = nueva_pieza()
                    sig_pieza, sig_color, _, _ = nueva_pieza()
                    puntos, lineas = 0, 0
                    game_over, pausa = False, False

                if not pausa and not game_over:
                    if evento.key == pygame.K_LEFT:
                        if not colision(tablero, pieza, px - 1, py):
                            px -= 1
                    elif evento.key == pygame.K_RIGHT:
                        if not colision(tablero, pieza, px + 1, py):
                            px += 1
                    elif evento.key == pygame.K_UP:
                        rotada = rotar(pieza)
                        for dx in [0, -1, 1, -2, 2]:
                            if not colision(tablero, rotada, px + dx, py):
                                pieza = rotada
                                px += dx
                                break
                    elif evento.key == pygame.K_DOWN:
                        if not colision(tablero, pieza, px, py + 1):
                            py += 1
                            puntos += 1
                    elif evento.key == pygame.K_SPACE:
                        while not colision(tablero, pieza, px, py + 1):
                            py += 1
                            puntos += 2
                        tiempo_caida = vel

        if not pausa and not game_over:
            if tiempo_caida >= vel:
                tiempo_caida = 0
                if not colision(tablero, pieza, px, py + 1):
                    py += 1
                else:
                    for r, fila in enumerate(pieza):
                        for c, val in enumerate(fila):
                            if val and py + r >= 0:
                                tablero[py + r][px + c] = color

                    nuevas_filas = [f for f in tablero if any(c is None for c in f)]
                    borradas = ROWS - len(nuevas_filas)
                    if borradas > 0:
                        tablero = [[None] * COLS for _ in range(borradas)] + nuevas_filas
                        lineas += borradas
                        puntos += [0, 100, 300, 500, 800][borradas]

                    pieza, color, px, py = sig_pieza, sig_color, (COLS - len(sig_pieza[0])) // 2, 0
                    sig_pieza, sig_color, _, _ = nueva_pieza()

                    if colision(tablero, pieza, px, py):
                        game_over = True

        # Renderizado
        pantalla.fill((20, 20, 28))

        # Rejilla y bloques colocados
        for f in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(c * CELL, f * CELL, CELL, CELL)
                pygame.draw.rect(pantalla, (32, 32, 45), rect, 1)
                if tablero[f][c]:
                    dibujar_bloque(pantalla, c * CELL, f * CELL, tablero[f][c])

        # Línea divisoria
        pygame.draw.line(pantalla, (60, 60, 85), (COLS * CELL, 0), (COLS * CELL, ALTO), 2)

        # Sombra de caída (Ghost piece)
        if not game_over:
            gy = py
            while not colision(tablero, pieza, px, gy + 1):
                gy += 1
            for r, fila in enumerate(pieza):
                for c, val in enumerate(fila):
                    if val:
                        s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
                        s.fill((*color, 60))
                        pantalla.blit(s, ((px + c) * CELL, (gy + r) * CELL))

            # Pieza activa
            for r, fila in enumerate(pieza):
                for c, val in enumerate(fila):
                    if val and py + r >= 0:
                        dibujar_bloque(pantalla, (px + c) * CELL, (py + r) * CELL, color)

        # Panel lateral con la siguiente pieza
        ox, oy = COLS * CELL + 25, 40
        pygame.draw.rect(pantalla, (28, 28, 40), (ox - 10, oy - 10, 120, 100), border_radius=6)
        for r, fila in enumerate(sig_pieza):
            for c, val in enumerate(fila):
                if val:
                    dibujar_bloque(pantalla, ox + c * CELL, oy + r * CELL, sig_color)

        # Mensaje GAME OVER centrado en el tablero
        if game_over:
            texto = fuente.render("GAME OVER", True, (255, 50, 60))
            pantalla.blit(texto, ((COLS * CELL - texto.get_width()) // 2, (ALTO - texto.get_height()) // 2))

        pygame.display.flip()

if __name__ == "__main__":
    main()
