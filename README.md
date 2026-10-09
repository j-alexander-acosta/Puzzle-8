# 🚀 8-Puzzle Espacial

Una reimaginación interactiva, gráfica y visualmente atractiva del clásico juego del "8-Puzzle" (rompecabezas de piezas deslizantes). Este proyecto toma una base algorítmica de búsqueda en grafos y la transforma en una experiencia amigable con temática espacial, animaciones fluidas y sonidos autogenerados.

## ✨ Características

- **Interfaz Gráfica (UI) Moderna**: Diseñada con Pygame, presenta un estilo neón/espacial con fichas coloridas, fuentes legibles y bordes redondeados, ideal para todas las edades.
- **Animaciones Fluidas**: Las piezas no "saltan" de golpe; se deslizan suavemente hacia el espacio vacío. Además, al ganar disfrutarás de un efecto de celebración con partículas (confeti).
- **Sonidos Autogenerados**: El juego incluye un pequeño sintetizador matemático interno que genera dinámicamente los efectos de sonido (`.wav`) de movimiento, error y victoria durante su primera ejecución. ¡No necesitas descargar assets de audio externos!
- **Auto-Resolución**: ¿Te has atascado? El botón de "Resolver Auto" utiliza el algoritmo *Breadth-First Search (BFS)* para encontrar la ruta óptima y anima la solución paso a paso frente a tus ojos.
- **Ingreso de Estado Manual**: Un menú interactivo que te permite introducir configuraciones de rompecabezas personalizadas, verificando en tiempo real que sean válidas y resolubles.
- **Barajado Inteligente**: El botón de "Nuevo Juego" baraja las fichas de forma aleatoria, pero garantizando matemáticamente (mediante el cálculo de paridad de inversiones) que el puzzle resultante siempre tenga solución.

## ⚙️ Requisitos

- **Python 3.x**
- **Pygame** (El script intentará instalar esta librería automáticamente si no la detecta).

## 🚀 Instalación y Ejecución

1. Abre tu terminal.
2. Navega hasta el directorio del proyecto:
   ```bash
   cd /Users/alexanderacosta/Documents/Proyectos/Puzzle-8
   ```
3. *(Opcional)* Si prefieres instalar la dependencia gráficamente tú mismo:
   ```bash
   pip install pygame
   ```
4. Ejecuta el archivo principal del juego:
   ```bash
   python puzzle_grafico.py
   ```
   *(Nota en Mac/Linux: Dependiendo de tu entorno, es posible que necesites ejecutar `python3 puzzle_grafico.py`).*

## 🎮 Cómo Jugar

- **Mover Piezas**: Haz clic izquierdo en cualquier pieza que esté inmediatamente adyacente (arriba, abajo, izquierda o derecha) al hueco oscurecido para deslizarla hacia allí.
- **Objetivo**: Ordena los números del **1 al 8** de izquierda a derecha y de arriba a abajo en la cuadrícula, dejando el espacio vacío (el 0) en la esquina inferior derecha.
- **Controles Inferiores**:
  - **Nuevo Juego**: Reinicia el tablero instantáneamente con un reto nuevo.
  - **Resolver Auto**: Cede el control a la computadora para que resuelva el estado actual.
  - **Estado Manual**: Abre una pantalla translúcida para que escribas una secuencia inicial (ej. `123456870`).
  - **Sonido (ON/OFF)**: Activa o silencia los efectos de audio.

## 🛠️ Archivos del Proyecto
- `puzzle_grafico.py`: Contiene tanto la lógica de búsqueda en grafos, como el generador de sonido y el motor gráfico de Pygame.
- `sfx_move.wav`, `sfx_error.wav`, `sfx_win.wav`: Archivos de sonido que el juego creará automáticamente en la carpeta la primera vez que lo abras.
