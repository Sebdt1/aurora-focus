# Aurora Focus

Un temporizador Pomodoro en Python puro, sin ninguna dependencia — solo tkinter, que ya viene con el intérprete. Nació como excusa para ver hasta dónde se puede estirar un Canvas de tkinter antes de que se vea feo, y terminó gustando más de lo esperado.

La idea es simple: el tiempo que queda es un anillo de luz que se va vaciando, rodeado de un puñado de partículas que orbitan y parpadean como estrellas. Cuando se acaba el tiempo el anillo pasa de azul a ámbar y después a rojo, y las partículas se aceleran — nada sutil, pero avisa sin sacarte de lo que estás haciendo. Al cerrar un ciclo, todo estalla en una lluvia de partículas y suena un beep.

Tiene los dos modos de siempre, enfoque y descanso, cada uno con su propia paleta de colores, y el descanso arranca solo en cuanto termina el enfoque para no tener que tocar nada. La duración se ajusta entre 5 y 60 minutos con los botones + y −, y el descanso se calcula como una fracción de esa duración. También cuenta cuántos ciclos completaste en la sesión, por si te gusta ver ese número subir.

## Cómo correrlo

Hace falta Python 3.8 o más nuevo, con tkinter (viene incluido en casi cualquier instalación estándar).

```bash
python aurora_focus.py
```

## Controles

Espacio inicia o pausa, R reinicia, + y − ajustan la duración del enfoque. Todo también funciona con clics si prefieres el mouse.

## Por dentro

Todo se dibuja cuadro por cuadro sobre un `tkinter.Canvas`, a unos 60 fps. Como tkinter no tiene canal alfa, el brillo y los halos son en el fondo una interpolación de colores hex hacia el color de fondo — un truco algo rudimentario, pero que funciona bien. El temporizador usa `time.monotonic()` en lugar de restar un contador en cada frame, para que no se desincronice si la animación tiene algún hipo.
