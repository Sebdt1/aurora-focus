# 🌌 Aurora Focus

Temporizador **Pomodoro** animado escrito en Python puro — sin dependencias externas, solo `tkinter` (incluido con Python).

El tiempo restante es un anillo de luz que se va consumiendo, rodeado de ~70 partículas que orbitan, parpadean como estrellas y se aceleran a medida que se agota el tiempo. Al completar un ciclo, estallan en una explosión de luces y la paleta cambia de color según el modo.

## ✨ Características

- **Anillo de progreso luminoso** con halo y punta brillante que recorre el círculo
- **Partículas orbitales** que reaccionan al tiempo: entran en frenesí en el tramo final mientras el anillo pasa de azul → ámbar → rojo
- **Explosión de partículas** y sonido al completar cada ciclo
- **Modos enfoque / descanso** con paletas propias (azul-violeta / verde-dorado); el descanso arranca solo al terminar el enfoque
- **Duración ajustable** de 5 a 60 minutos (el descanso se calcula proporcionalmente)
- **Contador de ciclos** completados en la sesión
- Fondo de estrellas titilantes, botones con hover y reloj que "respira"

## 🚀 Uso

Requiere Python 3.8+ (con tkinter, que viene incluido en la instalación estándar).

```bash
python aurora_focus.py
```

## ⌨️ Controles

| Tecla / acción | Función |
|---|---|
| `Espacio` | Iniciar / pausar |
| `R` | Reiniciar |
| `+` / `−` | Ajustar duración del enfoque |
| Clic | Todos los controles también funcionan con el mouse |

## 🖼️ Cómo funciona

Todo se dibuja a ~60 fps sobre un `tkinter.Canvas`: el brillo y los halos se simulan interpolando colores hex hacia el fondo (tkinter no tiene canal alfa), las partículas orbitan con oscilación radial senoidal, y el temporizador usa `time.monotonic()` para no perder precisión aunque la animación fluctúe.
