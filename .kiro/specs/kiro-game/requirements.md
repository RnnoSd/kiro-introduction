# Requirements Document

## Introduction

"Flappy Kiro" es un juego 2D de desplazamiento horizontal desarrollado en Python. El jugador controla a Kiro (un fantasma) navegando por un escenario de scroll infinito, esquivando obstáculos, recolectando bonificaciones y atravesando barras verticales para acumular puntos. El juego combina mecánicas de movimiento fluido con valores numéricos precisos, poderes especiales con cooldown, sistema de vidas dinámico con bonificaciones y penalizaciones, y retroalimentación audiovisual para ofrecer una experiencia arcade desafiante.

---

## Glossary

- **Kiro**: El personaje principal controlado por el jugador, representado por el sprite `ghosty.png`.
- **Motor_de_Juego**: El subsistema principal responsable del bucle de juego, actualización de estado y renderizado.
- **Sistema_de_Puntuación**: El subsistema que gestiona el puntaje, vidas y condiciones de bonificación.
- **Gestor_de_Objetos**: El subsistema responsable de crear, mover y destruir los objetos del escenario.
- **Gestor_de_Audio**: El subsistema que carga y reproduce efectos de sonido.
- **Barra_Verde**: Obstáculo vertical de color verde que aparece en pares con un hueco entre ellos, similar a las tuberías en juegos tipo Flappy Bird.
- **Objeto_Rojo**: Objeto móvil de color rojo que penaliza al jugador con -20 puntos al colisionar.
- **Objeto_Verde**: Objeto móvil de color verde que bonifica al jugador con +100 puntos al colisionar.
- **Proyectil**: Objeto disparado por Kiro con la tecla A que destruye Objetos_Rojos al impactarlos.
- **Cooldown**: Período de enfriamiento tras usar una habilidad especial, durante el cual dicha habilidad no puede volver a activarse.
- **Scroll**: Desplazamiento continuo y repetido del fondo de pantalla de derecha a izquierda.
- **HUD**: Interfaz gráfica superpuesta que muestra puntuación y vidas al jugador en tiempo real.
- **Pantalla_de_Game_Over**: Pantalla mostrada al finalizar la partida con la puntuación final del jugador y opciones de reinicio o salida.

---

## Requirements

### Requirement 1: Movimiento del Personaje

**User Story:** Como jugador, quiero controlar a Kiro con las teclas de dirección, para navegar libremente por el escenario.

#### Acceptance Criteria

1. WHEN el jugador presiona la tecla de flecha ARRIBA sin presionar BARRA ESPACIADORA, THE Motor_de_Juego SHALL mover a Kiro hacia arriba a 5 píxeles por frame.
2. WHEN el jugador presiona la tecla de flecha ABAJO sin presionar BARRA ESPACIADORA, THE Motor_de_Juego SHALL mover a Kiro hacia abajo a 5 píxeles por frame.
3. WHEN el jugador presiona la tecla de flecha IZQUIERDA sin presionar BARRA ESPACIADORA, THE Motor_de_Juego SHALL mover a Kiro hacia la izquierda a 5 píxeles por frame.
4. WHEN el jugador presiona la tecla de flecha DERECHA sin presionar BARRA ESPACIADORA, THE Motor_de_Juego SHALL mover a Kiro hacia la derecha a 5 píxeles por frame.
5. WHILE el jugador mantiene presionada la BARRA ESPACIADORA y una tecla de dirección simultáneamente, THE Motor_de_Juego SHALL aplicar a Kiro una velocidad de 10 píxeles por frame en esa dirección.
6. WHEN el jugador suelta la BARRA ESPACIADORA mientras mantiene una tecla de dirección, THE Motor_de_Juego SHALL restaurar la velocidad de Kiro a 5 píxeles por frame en el siguiente frame.
7. WHEN el movimiento de Kiro llevaría cualquier parte de su sprite fuera de los límites visibles de la pantalla, THE Motor_de_Juego SHALL detener el desplazamiento en ese eje y mantener a Kiro en el borde de la pantalla.
8. WHEN el jugador presiona dos teclas de dirección ortogonales simultáneamente (por ejemplo, ARRIBA e IZQUIERDA), THE Motor_de_Juego SHALL aplicar ambos vectores de velocidad de forma independiente, resultando en movimiento diagonal.

---

### Requirement 2: Escenario con Scroll Infinito

**User Story:** Como jugador, quiero que el fondo se desplace continuamente, para sentir que Kiro avanza por un mundo sin fin.

#### Acceptance Criteria

1. WHEN el juego está en estado activo, THE Motor_de_Juego SHALL renderizar el fondo usando dos copias de la imagen `img/example-ui.png` posicionadas consecutivamente en el eje X, desplazándose de derecha a izquierda a una velocidad constante.
2. WHEN el borde izquierdo de la primera copia del fondo alcanza el borde izquierdo de la pantalla, THE Motor_de_Juego SHALL reposicionar esa copia inmediatamente a la derecha de la segunda copia, garantizando continuidad visual sin saltos.
3. WHEN el estado de Kiro es Freno (habilidad S activa), THE Motor_de_Juego SHALL continuar desplazando el fondo a la misma velocidad que cuando Kiro se mueve con normalidad.

---

### Requirement 3: Barras Verdes Verticales

**User Story:** Como jugador, quiero que aparezcan pares de barras verdes verticales con un hueco entre ellas, para intentar pasar por el espacio y ganar puntos.

#### Acceptance Criteria

1. WHILE el juego está en estado activo, THE Gestor_de_Objetos SHALL mantener al menos un par de Barras_Verdes desplazándose de derecha a izquierda a la misma velocidad que el Scroll del fondo.
2. WHEN se genera un par de Barras_Verdes, THE Gestor_de_Objetos SHALL posicionar las barras dejando un hueco de entre 150 y 200 píxeles de alto, cuya posición vertical se determina aleatoriamente dentro de los límites de la pantalla.
3. WHEN el borde izquierdo del sprite de Kiro supera el borde derecho de un par de Barras_Verdes sin que haya ocurrido una colisión con ese par, THE Sistema_de_Puntuación SHALL incrementar la puntuación del jugador en 5 puntos.
4. WHEN el bounding box de Kiro se superpone con el bounding box de una Barra_Verde, THE Sistema_de_Puntuación SHALL decrementar las vidas del jugador en 1 y THE Motor_de_Juego SHALL activar un período de invulnerabilidad de 1 segundo durante el cual nuevas colisiones con Barras_Verdes no restan vidas.
5. WHEN la distancia entre el par de Barras_Verdes más a la derecha y el borde derecho de la pantalla es mayor o igual a 200 píxeles, THE Gestor_de_Objetos SHALL generar un nuevo par de Barras_Verdes en el borde derecho de la pantalla.
6. WHEN un par de Barras_Verdes sale completamente por el borde izquierdo de la pantalla, THE Gestor_de_Objetos SHALL eliminar ese par de la memoria.

---

### Requirement 4: Sistema de Puntuación y Vidas

**User Story:** Como jugador, quiero ver mi puntuación y vidas en pantalla, para saber mi progreso y cuántas oportunidades me quedan.

#### Acceptance Criteria

1. WHEN el Motor_de_Juego inicia una nueva partida, THE Sistema_de_Puntuación SHALL establecer las vidas del jugador en 3 y la puntuación en 0.
2. WHILE el juego está en estado activo, THE Motor_de_Juego SHALL mostrar la puntuación actual y el número de vidas restantes en el HUD de forma legible en todo momento.
3. WHEN la puntuación del jugador incrementa y el nuevo total es un múltiplo exacto de 1000 (por ejemplo, 1000, 2000, 3000) y el total de vidas no supera 9, THE Sistema_de_Puntuación SHALL incrementar las vidas del jugador en 1.
4. WHEN el Sistema_de_Puntuación incrementa las vidas del jugador por bonificación, THE Gestor_de_Audio SHALL reproducir el sonido `assets/jump.wav`.
5. WHEN una penalización de puntos reduciría la puntuación del jugador por debajo de 0, THE Sistema_de_Puntuación SHALL establecer la puntuación en 0 y decrementar las vidas del jugador en 1.
6. WHEN la puntuación del jugador es exactamente 0 y ocurre una penalización de puntos adicional, THE Sistema_de_Puntuación SHALL decrementar las vidas del jugador en 1 sin alterar la puntuación.
7. THE Sistema_de_Puntuación SHALL mantener la puntuación del jugador en un valor mínimo de 0 en todo momento.

---

### Requirement 5: Objetos Móviles (Rojos y Verdes)

**User Story:** Como jugador, quiero que aparezcan objetos de distintos colores moviéndose por la pantalla, para ganar o perder puntos al interactuar con ellos.

#### Acceptance Criteria

1. WHILE el juego está en estado activo, THE Gestor_de_Objetos SHALL mantener en pantalla al menos 1 Objeto_Rojo y 1 Objeto_Verde desplazándose de derecha a izquierda a una velocidad entre 3 y 8 píxeles por frame, independientemente uno del otro.
2. WHEN el bounding box de Kiro se superpone con el bounding box de un Objeto_Rojo, THE Sistema_de_Puntuación SHALL decrementar la puntuación del jugador en 20 puntos sin que la puntuación pueda ser inferior a 0.
3. WHEN el bounding box de Kiro se superpone con el bounding box de un Objeto_Rojo, THE Gestor_de_Audio SHALL reproducir el sonido `assets/game_over.wav` sin interrumpir la partida en curso.
4. WHEN el bounding box de Kiro se superpone con el bounding box de un Objeto_Verde, THE Sistema_de_Puntuación SHALL incrementar la puntuación del jugador en 100 puntos.
5. WHEN el borde derecho de un Objeto_Rojo o Objeto_Verde sale por el borde izquierdo de la pantalla, THE Gestor_de_Objetos SHALL reposicionar el objeto en el borde derecho de la pantalla con una coordenada Y aleatoria dentro de los límites visibles.
6. WHEN el bounding box de Kiro se superpone con el bounding box de un Objeto_Verde, THE Gestor_de_Audio SHALL reproducir un sonido de bonificación.

---

### Requirement 6: Poder - Disparo (Tecla A)

**User Story:** Como jugador, quiero disparar un proyectil con la tecla A para destruir Objetos_Rojos y evitar penalizaciones.

#### Acceptance Criteria

1. WHEN el jugador presiona la tecla A y el Cooldown del disparo ha expirado, THE Motor_de_Juego SHALL instanciar un Proyectil en el borde derecho del sprite de Kiro que se desplaza hacia la derecha a 400 píxeles por segundo.
2. WHEN el bounding box de un Proyectil se superpone con el bounding box de un Objeto_Rojo, THE Gestor_de_Objetos SHALL eliminar el Objeto_Rojo y el Proyectil de la pantalla en el mismo frame.
3. WHEN un Proyectil sale por el borde derecho de la pantalla sin haber impactado ningún objeto, THE Motor_de_Juego SHALL eliminar el Proyectil de la memoria.
4. WHILE el Cooldown del disparo está activo, THE Motor_de_Juego SHALL ignorar nuevas pulsaciones de la tecla A para el disparo.
5. WHEN el jugador dispara un Proyectil, THE Motor_de_Juego SHALL activar el Cooldown del disparo por 500 milisegundos, durante los cuales no se pueden generar nuevos Proyectiles.

---

### Requirement 7: Poder - Retroceso (Tecla W)

**User Story:** Como jugador, quiero retroceder instantáneamente 100 píxeles con la tecla W para esquivar obstáculos de forma reactiva.

#### Acceptance Criteria

1. WHEN el jugador presiona la tecla W y el Cooldown del retroceso ha expirado, THE Motor_de_Juego SHALL desplazar la posición X de Kiro 100 píxeles hacia la izquierda en el mismo ciclo de actualización del juego en que se registra la pulsación.
2. WHEN el retroceso llevaría la coordenada X de Kiro a un valor menor que 0, THE Motor_de_Juego SHALL establecer la coordenada X de Kiro en 0, preservando su coordenada Y sin cambios.
3. WHILE el Cooldown del retroceso está activo, THE Motor_de_Juego SHALL ignorar nuevas pulsaciones de la tecla W para el retroceso.
4. THE Motor_de_Juego SHALL establecer un Cooldown de 1000 milisegundos para el retroceso tras cada uso.
5. WHEN el Motor_de_Juego inicia una nueva partida, THE Motor_de_Juego SHALL inicializar el Cooldown del retroceso como expirado, permitiendo su uso inmediato.

---

### Requirement 8: Poder - Freno (Tecla S)

**User Story:** Como jugador, quiero frenar a Kiro con la tecla S para tener más control en situaciones de peligro.

#### Acceptance Criteria

1. WHEN el jugador presiona la tecla S y el Cooldown del freno ha expirado, THE Motor_de_Juego SHALL establecer la velocidad de movimiento de Kiro a 0 píxeles por frame durante los próximos 3 segundos.
2. WHILE el freno está activo, THE Motor_de_Juego SHALL continuar desplazando el fondo del Scroll y actualizando la posición de todos los Objetos_Rojos, Objetos_Verdes y Barras_Verdes en cada frame.
3. WHEN transcurren 3 segundos desde la activación del freno, THE Motor_de_Juego SHALL restaurar la velocidad de movimiento de Kiro a 5 píxeles por frame.
4. WHEN el jugador activa el freno, THE Motor_de_Juego SHALL iniciar un Cooldown de 5000 milisegundos, durante los cuales nuevas pulsaciones de la tecla S no activarán el freno.
5. WHEN el jugador presiona la tecla S y el Cooldown del freno está activo, THE Motor_de_Juego SHALL ignorar la pulsación sin ningún efecto visible sobre Kiro.

---

### Requirement 9: Retroalimentación de Audio

**User Story:** Como jugador, quiero escuchar efectos de sonido ante eventos importantes del juego, para recibir retroalimentación inmediata de mis acciones.

#### Acceptance Criteria

1. WHEN el Motor_de_Juego inicia, THE Gestor_de_Audio SHALL intentar cargar los archivos `assets/jump.wav` y `assets/game_over.wav`.
2. WHEN el Sistema_de_Puntuación incrementa las vidas del jugador por bonificación de puntos, THE Gestor_de_Audio SHALL reproducir el sonido cargado desde `assets/jump.wav`.
3. WHEN el bounding box de Kiro se superpone con el bounding box de un Objeto_Rojo, THE Gestor_de_Audio SHALL reproducir el sonido cargado desde `assets/game_over.wav`.
4. IF `assets/jump.wav` no puede ser cargado, THEN THE Gestor_de_Audio SHALL deshabilitar únicamente los sonidos asociados a ese archivo y continuar reproduciendo los demás sonidos disponibles sin interrumpir la partida.
5. IF `assets/game_over.wav` no puede ser cargado, THEN THE Gestor_de_Audio SHALL deshabilitar únicamente los sonidos asociados a ese archivo y continuar reproduciendo los demás sonidos disponibles sin interrumpir la partida.

---

### Requirement 10: Condición de Fin de Partida

**User Story:** Como jugador, quiero que el juego termine y muestre mi puntuación cuando pierdo todas mis vidas, para saber cómo me fue en la partida.

#### Acceptance Criteria

1. WHEN las vidas del jugador llegan a 0, THE Motor_de_Juego SHALL detener el bucle de juego activo y mostrar la Pantalla_de_Game_Over en el siguiente frame.
2. WHEN la Pantalla_de_Game_Over es visible, THE Motor_de_Juego SHALL mostrar la puntuación final obtenida por el jugador durante la partida en un texto claramente legible.
3. WHEN la Pantalla_de_Game_Over es visible, THE Motor_de_Juego SHALL mostrar dos opciones seleccionables por el jugador: "Reiniciar" y "Salir".
4. WHEN el jugador selecciona "Reiniciar" en la Pantalla_de_Game_Over, THE Motor_de_Juego SHALL reinicializar el estado del juego con 3 vidas y 0 puntos y reanudar el bucle de juego activo.
5. WHEN el jugador selecciona "Salir" en la Pantalla_de_Game_Over, THE Motor_de_Juego SHALL cerrar la aplicación.
