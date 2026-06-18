# Implementation Plan: Flappy Kiro — Endless Runner

## Overview

Implementación incremental del juego Flappy Kiro en Python/pygame. Cada tarea construye sobre la anterior, partiendo de la estructura base, los modelos de datos y los servicios de bajo nivel, hasta llegar a la integración completa del bucle de juego.

## Tasks

- [x] 1. Configurar estructura del proyecto y modelos de datos base
  - Crear `main.py` como punto de entrada con manejo de `FileNotFoundError` y cierre limpio de pygame
  - Crear `src/config.py` con los dataclasses `CanvasConfig`, `PlayerConfig`, `BarsConfig`, `ObjectsConfig`, `ProjectileConfig`, `ScoreConfig`, `BackgroundConfig` y `GameConfig` con los valores por defecto indicados en el diseño
  - Crear `src/models.py` con `Vector2`, `Rect` y la función `rects_overlap(a, b)`
  - Crear `src/state.py` con el enum `State` (`IDLE`, `PLAYING`, `GAME_OVER`)
  - Configurar `requirements.txt` con `pygame` y `requirements-dev.txt` con `pytest` y `hypothesis`
  - _Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10_

  - [x] 1.1 Implementar modelos de datos (`Vector2`, `Rect`, `rects_overlap`)
    - Escribir los dataclasses y la función de detección de solapamiento AABB
    - _Requirements: 3.4, 5.2, 5.4, 6.2_

  - [ ]* 1.2 Escribir tests unitarios para `rects_overlap`
    - Casos: solapamiento parcial, total, sin solapamiento, bordes que se tocan (no colisión)
    - _Requirements: 3.4, 5.2_

  - [ ]* 1.3 Escribir property test para conmutatividad de `rects_overlap`
    - **Property 6: Conmutatividad de detección de colisiones**
    - **Validates: Requirements 3, 5, 6**

  - [x] 1.4 Implementar `GameConfig` con todos los sub-dataclasses y valores por defecto
    - _Requirements: 1.1–1.8, 6.1, 6.5, 7.1, 7.4, 8.1, 8.4_

  - [ ]* 1.5 Escribir tests unitarios para `GameConfig` — valores por defecto en rangos válidos
    - Verificar que `base_speed < boost_speed`, `gap_size_min < gap_size_max`, cooldowns positivos
    - _Requirements: 1.1, 1.5, 3.2_

- [x] 2. Implementar `AssetLoader` y `AudioService`
  - [x] 2.1 Implementar `AssetLoader` con carga de imágenes y audio
    - Crear `src/asset_loader.py` con `AssetManifest`, `AssetCache` y `AssetLoader.load()`
    - Usar `pygame.image.load().convert_alpha()` para imágenes
    - Lanzar `FileNotFoundError` si falta `ghosty.png` o `example-ui.png`
    - _Requirements: 9.1_

  - [x] 2.2 Implementar `AudioService` con degradación silenciosa
    - Crear `src/audio_service.py` con `AudioService.play_jump()` y `AudioService.play_penalty()`
    - Capturar excepciones por archivo; deshabilitar solo el sonido afectado
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ]* 2.3 Escribir tests unitarios para `AudioService`
    - Test: audio faltante deshabilita ese sonido sin afectar los demás
    - Test: `play_jump()` y `play_penalty()` no lanzan excepciones aunque el mixer no esté disponible
    - _Requirements: 9.4, 9.5_

- [x] 3. Implementar `InputHandler`
  - [x] 3.1 Crear `src/input_handler.py` con `InputHandler`
    - Mantener `keys_held` con eventos `KEYDOWN`/`KEYUP`
    - Retornar acciones discretas: `'shoot'`, `'dash'`, `'brake'`, `'restart'`, `'quit'`
    - Implementar `get_movement_vector()` e `is_boost_active()`
    - _Requirements: 1.1–1.8, 6.1, 7.1, 8.1, 10.4, 10.5_

  - [ ]* 3.2 Escribir tests unitarios para `InputHandler`
    - Test: `get_movement_vector()` con combinaciones de teclas incluyendo diagonal
    - Test: `is_boost_active()` con y sin ESPACIO
    - Test: acciones de un solo disparo generadas correctamente
    - _Requirements: 1.3, 1.4, 1.8_

- [x] 4. Implementar `Background`
  - [x] 4.1 Crear `src/background.py` con `Background`
    - Doble buffer con dos copias de `example-ui.png`
    - `update(delta_time)`: avanzar `scroll_x`; reposicionar copia que sale por la izquierda
    - `render(surface)`: dibujar ambas copias sin brecha visible
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 4.2 Escribir property test para continuidad del scroll
    - **Property 7: Scroll del fondo continuo sin saltos**
    - **Validates: Requirements 2**
    - Verificar que para cualquier `scroll_x`, la suma de cobertura de ambas copias cubre el canvas sin brecha

- [x] 5. Implementar `Player`
  - [x] 5.1 Crear `src/player.py` con la clase `Player`
    - Movimiento en 4 direcciones con velocidad base (5 px/frame) y boost (10 px/frame)
    - Movimiento diagonal: aplicar vectores X e Y de forma independiente
    - Clamping de posición a límites del canvas en cada frame
    - Decrementar `brake_timer`, `cooldown_*` e `invulnerable_timer` cada frame
    - _Requirements: 1.1–1.8_

  - [x] 5.2 Implementar habilidades especiales en `Player`
    - `try_shoot()`: retorna `Projectile` si cooldown expirado, activa cooldown 500ms
    - `try_dash_back()`: desplaza X −100px (mín 0), activa cooldown 1000ms
    - `try_brake()`: activa `is_braking` durante 3s, activa cooldown 5000ms
    - `reset()`: restaura posición inicial y limpia todos los cooldowns
    - _Requirements: 6.1, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 5.3 Escribir tests unitarios para `Player`
    - Test: velocidad base vs boost; velocidad 0 en estado `is_braking`
    - Test: `try_shoot()` con cooldown expirado vs activo
    - Test: `try_dash_back()` clampea a x=0 si posición < 100
    - Test: clamping de posición en todos los bordes del canvas
    - _Requirements: 1.1, 1.5, 1.7, 6.1, 6.4, 7.1, 7.2, 8.1_

  - [ ]* 5.4 Escribir property test para velocidad acotada de Kiro
    - **Property 1: Velocidad de Kiro acotada**
    - **Validates: Requirements 1, 8**
    - Para cualquier `delta_time` en `[0, 0.1]`, la velocidad nunca supera `boost_speed`; con `is_braking=True` la velocidad es exactamente 0

  - [ ]* 5.5 Escribir property test para Kiro siempre dentro del canvas
    - **Property 2: Kiro siempre dentro del canvas**
    - **Validates: Requirements 1, 7**
    - Para cualquier secuencia de inputs, `0 ≤ x ≤ canvas.width - sprite_width` y `0 ≤ y ≤ canvas.height - sprite_height`

- [x] 6. Checkpoint — Asegurar que todos los tests pasan hasta aquí
  - Ejecutar `pytest` y verificar que pasan los tests de modelos, config, audio, input, background y player
  - Preguntar al usuario si hay dudas antes de continuar.

- [x] 7. Implementar `ScoreTracker`
  - [x] 7.1 Crear `src/score_tracker.py` con la clase `ScoreTracker`
    - `add_points(amount)`: suma puntos; dispara bonus de vida al cruzar múltiplo de 1000 (máx 9 vidas)
    - `deduct_points(amount)`: resta puntos; si llega a 0 o menos, fija en 0 y llama `lose_life()`
    - `lose_life()`: decrementa vidas en 1
    - `reset()`: reinicia `score=0`, `lives=3`, `_last_bonus_threshold=0`
    - `render(surface)`: dibuja HUD con puntuación y vidas
    - Puntuación mínima siempre 0; cap de vidas en 9
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ]* 7.2 Escribir tests unitarios para `ScoreTracker`
    - Test: `add_points` cruza umbral 1000 exactamente una vez → +1 vida
    - Test: bonus de vida no se aplica si `lives == 9`
    - Test: `deduct_points` con score > penalización, score == penalización, score < penalización
    - Test: penalización cuando score ya es 0 → pierde vida sin alterar score
    - _Requirements: 4.3, 4.5, 4.6, 4.7_

  - [ ]* 7.3 Escribir property test para puntuación nunca negativa
    - **Property 3: Puntuación nunca negativa**
    - **Validates: Requirements 4, 5**
    - Para cualquier secuencia de `add_points`/`deduct_points`, `score >= 0` es invariante

  - [ ]* 7.4 Escribir property test para vidas acotadas entre 0 y 9
    - **Property 4: Vidas acotadas entre 0 y 9**
    - **Validates: Requirements 4**
    - `0 ≤ lives ≤ 9` es invariante tras cualquier operación

  - [ ]* 7.5 Escribir property test para bonus de vida exactamente una vez por umbral
    - **Property 5: Bonus de vida exactamente una vez por umbral**
    - **Validates: Requirements 4**
    - Para cualquier umbral `k * 1000` cruzado exactamente una vez, se otorga exactamente 1 vida adicional

- [x] 8. Implementar `BarManager`
  - [x] 8.1 Crear `src/bar_manager.py` con `BarPair` y `BarManager`
    - `update(delta_time)`: desplazar barras a `scroll_speed` px/s; generar nuevo par si distancia al borde derecho ≥ 200px; eliminar pares fuera de pantalla
    - Aleatorizar `gap_y` dentro de `[min_gap_y, max_gap_y]`; `gap_size` entre 150–200px
    - Marcar `scored=True` cuando el borde izquierdo de Kiro supera el borde derecho del par
    - `render(surface)`: dibujar barras en verde
    - `reset()`: eliminar todos los pares activos
    - _Requirements: 3.1, 3.2, 3.5, 3.6_

  - [ ]* 8.2 Escribir tests unitarios para `BarManager`
    - Test: se genera nuevo par cuando la distancia al borde derecho ≥ 200px
    - Test: par eliminado cuando sale completamente por el borde izquierdo
    - Test: `gap_size` siempre entre 150 y 200px
    - _Requirements: 3.1, 3.2, 3.5, 3.6_

- [x] 9. Implementar `ObjectManager`
  - [x] 9.1 Crear `src/object_manager.py` con `GameObject` y `ObjectManager`
    - Inicializar al menos 1 `Objeto_Rojo` y 1 `Objeto_Verde` con velocidades aleatorias entre 3–8 px/frame
    - `update(delta_time)`: desplazar cada objeto a su velocidad propia; reposicionar en borde derecho con Y aleatoria al salir por la izquierda
    - `render(surface)`: dibujar objetos (rojo/verde según tipo)
    - `reset()`: reiniciar posiciones de todos los objetos
    - _Requirements: 5.1, 5.5_

  - [ ]* 9.2 Escribir tests unitarios para `ObjectManager`
    - Test: al menos 1 objeto rojo y 1 verde siempre activos
    - Test: objeto reposicionado en borde derecho al salir por la izquierda
    - Test: velocidades en rango `[3, 8]` px/frame
    - _Requirements: 5.1, 5.5_

- [x] 10. Implementar `ProjectileManager`
  - [x] 10.1 Crear `src/projectile_manager.py` con `Projectile` y `ProjectileManager`
    - `spawn(origin)`: instanciar proyectil en el borde derecho del sprite de Kiro
    - `update(delta_time, red_objects)`: mover proyectiles a 400 px/s hacia la derecha; detectar colisión con objetos rojos; eliminar proyectil y objeto rojo en el mismo frame; eliminar proyectiles fuera del borde derecho
    - `render(surface)`: dibujar proyectiles como barras horizontales
    - `reset()`: eliminar todos los proyectiles activos
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ]* 10.2 Escribir tests unitarios para `ProjectileManager`
    - Test: proyectil eliminado al salir por el borde derecho
    - Test: proyectil y objeto rojo eliminados en el mismo frame al colisionar
    - Test: proyectil no interactúa con objetos verdes ni barras
    - _Requirements: 6.2, 6.3_

- [x] 11. Checkpoint — Asegurar que todos los tests pasan hasta aquí
  - Ejecutar `pytest` y verificar que pasan los tests de score, barras, objetos y proyectiles
  - Preguntar al usuario si hay dudas antes de continuar.

- [x] 12. Implementar `StateManager` y lógica de colisiones
  - [x] 12.1 Crear `src/state_manager.py` con `StateManager`
    - Orquestar `tick(delta_time)`: actualizar `Background`, `Player`, `BarManager`, `ObjectManager`, `ProjectileManager`, `ScoreTracker` solo en estado `PLAYING`
    - Detección de colisiones: Kiro↔Barras (con invulnerabilidad), Kiro↔ObjetosRojos, Kiro↔ObjetosVerdes, Proyectil↔ObjetosRojos
    - Disparar transición a `GAME_OVER` cuando `ScoreTracker.lives == 0`
    - `on_restart()`: reiniciar todos los subsistemas y transicionar a `PLAYING`
    - `on_quit()`: cerrar aplicación limpiamente
    - _Requirements: 3.3, 3.4, 4.3, 4.4, 4.5, 4.6, 5.2, 5.3, 5.4, 5.6, 6.2, 10.1_

  - [x] 12.2 Integrar `AudioService` en colisiones y eventos de score
    - `ScoreTracker.add_points()` notifica a `AudioService.play_jump()` al ganar vida
    - Colisión Kiro↔ObjetoRojo notifica a `AudioService.play_penalty()`
    - Colisión Kiro↔ObjetoVerde notifica a `AudioService.play_jump()`
    - _Requirements: 4.4, 5.3, 5.6, 9.2, 9.3_

  - [ ]* 12.3 Escribir property test para invulnerabilidad impide pérdidas múltiples
    - **Property 8: Invulnerabilidad impide pérdidas de vida múltiples**
    - **Validates: Requirements 3**
    - Durante el período de invulnerabilidad de 1s, ninguna colisión adicional con Barras_Verdes decrementa las vidas

  - [ ]* 12.4 Escribir tests de integración para flujos críticos
    - Test: Kiro atraviesa hueco entre barras → score +5
    - Test: `lives=1` → colisión con barra → `lives=0` → estado `GAME_OVER`
    - Test: estado `GAME_OVER` → `on_restart()` → `score=0`, `lives=3`, estado `PLAYING`
    - Test: proyectil colisiona con objeto rojo → ambos eliminados del mismo frame
    - Test: score cruza 1000 → `lives+1`, `play_jump()` invocado
    - _Requirements: 3.3, 3.4, 4.3, 5.2, 6.2, 10.1, 10.4_

- [x] 13. Implementar `GameLoop` y pantalla de inicio
  - [x] 13.1 Crear `src/game_loop.py` con `GameLoop`
    - Inicializar pygame, crear ventana con dimensiones de `CanvasConfig`
    - `start()`: bucle principal con `Clock.tick(60)`; calcular delta time en segundos, capado a 0.1s
    - Pasar eventos pygame al `InputHandler`; despachar `state_manager.tick(delta_time)` cada frame
    - Manejar `pygame.QUIT` llamando `stop()` → `pygame.quit()`
    - _Requirements: 1, 2, 6, 7, 8, 10_

  - [x] 13.2 Implementar pantalla IDLE y pantalla GAME_OVER en el `Renderer`
    - Estado `IDLE`: mostrar mensaje "Presiona ENTER para empezar"
    - Estado `GAME_OVER`: mostrar puntuación final + opciones "Reiniciar" y "Salir" seleccionables
    - Estado `PLAYING`: renderizar en orden Z: fondo → barras → objetos → proyectiles → Kiro → HUD
    - _Requirements: 10.2, 10.3, 10.4, 10.5_

- [x] 14. Cablear todos los componentes en `main.py`
  - [x] 14.1 Ensamblar el juego completo en `main.py`
    - Instanciar `GameConfig`, `AssetLoader`, `AudioService`, `InputHandler`
    - Instanciar `Background`, `Player`, `BarManager`, `ObjectManager`, `ProjectileManager`, `ScoreTracker`
    - Instanciar `StateManager` con todos los subsistemas
    - Instanciar `GameLoop` y llamar `start()`
    - Capturar `FileNotFoundError` de `AssetLoader` e imprimir error descriptivo antes de cerrar
    - _Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10_

- [x] 15. Checkpoint final — Asegurar que todos los tests pasan
  - Ejecutar `pytest` y verificar que pasan todos los tests (unitarios, property-based, integración)
  - Preguntar al usuario si hay dudas antes de declarar el juego completo.

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia requirements específicos para trazabilidad
- Los property tests usan `hypothesis` y corresponden a las propiedades definidas en el diseño
- Los tests unitarios usan `pytest` puro sin pygame (lógica pura)
- Los checkpoints aseguran validación incremental antes de continuar
- La física usa delta-time para comportamiento consistente a cualquier tasa de frames
- Todos los valores numéricos se leen de `GameConfig`; no hay constantes hardcodeadas

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.4"] },
    { "id": 1, "tasks": ["1.2", "1.3", "1.5", "2.1"] },
    { "id": 2, "tasks": ["2.2", "3.1", "4.1"] },
    { "id": 3, "tasks": ["2.3", "3.2", "4.2", "5.1"] },
    { "id": 4, "tasks": ["5.2", "7.1", "8.1", "9.1", "10.1"] },
    { "id": 5, "tasks": ["5.3", "5.4", "5.5", "7.2", "7.3", "7.4", "7.5", "8.2", "9.2", "10.2"] },
    { "id": 6, "tasks": ["12.1"] },
    { "id": 7, "tasks": ["12.2", "12.3", "12.4"] },
    { "id": 8, "tasks": ["13.1"] },
    { "id": 9, "tasks": ["13.2"] },
    { "id": 10, "tasks": ["14.1"] }
  ]
}
```
