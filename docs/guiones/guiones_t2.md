# Guiones — Tarea 2: Llamadas de venta (restaurante) — SET B

Dominio: **Restaurante** — Chifa Dragón Dorado (inventado). A = vendedora · B = clienta. Todo lo dicho es INVENTADO.

## Carta y promociones (para el validador aritmético)

| Producto | Tamaño | Precio (S/) |
|---|---|---|
| arroz chaufa | personal | 18 |
| arroz chaufa | familiar | 34 |
| tallarín saltado | unico | 22 |
| wantán frito | porción | 12 |
| sopa de wantán | unico | 16 |
| gaseosa | personal | 5 |
| limonada | jarra | 14 |

- **Q1:** descuento de quince soles en pedidos desde noventa soles (resta 15 si el subtotal es >= 90).
- **Q2:** tres por dos en gaseosas personales (por cada 3 gaseosas personales, 1 es gratis (resta 5)).

## Trampas plantadas

| Clip | Autocorrección | Total incorrecto | Dirección con dígitos | Total dicho | Total correcto |
|---|---|---|---|---|---|
| t2_01 | — | — | sí | 68 | 68 |
| t2_02 | sí | sí | sí | 72 | 62 |
| t2_03 | sí | — | — | 113 | 113 |
| t2_04 | — | sí | sí | 76 | 71 |
| t2_05 | sí | sí | sí | 148 | 143 |

---

## t2_01  (llamada)

- Palabras: 426 · duración estimada: ~3.4 min
- Trampas: Llamada base, total correcto. SIN promoción aplicada (se menciona que no aplica: promocion = null). Dirección con dígitos.

**A:** Chifa Dragón Dorado, buenas tardes, ¿en qué le puedo ayudar?

**B:** Buenas tardes, quisiera hacer un pedido para delivery, por favor.

**A:** Claro que sí, cuénteme qué desea pedir.

**B:** Quiero un arroz chaufa familiar, un tallarín saltado y una porción de wantán frito.

**A:** Perfecto. El arroz chaufa familiar cuesta treinta y cuatro soles, el tallarín saltado veintidós soles y la porción de wantán frito doce soles. ¿Algo más?

**B:** No, eso es todo. Una consulta, ¿el tallarín saltado lleva carne o pollo?

**A:** Puede ser de pollo, de carne o mixto. ¿Cuál prefiere?

**B:** Mixto, por favor. ¿Y el wantán frito viene con salsa?

**A:** Sí, con salsa de tamarindo, que es agridulce.

**B:** Perfecto. ¿El chaufa familiar alcanza para tres personas?

**A:** Sí, alcanza bien para tres, y si comen poco hasta para cuatro.

**B:** Genial. ¿Y pueden enviarme también salsa de ají y sillao?

**A:** Claro, con gusto, le incluimos sobrecitos de sillao y de ají.

**B:** Gracias.

**A:** Si lo desea, también podemos enviar cucharas y tenedores descartables, además de los palitos.

**B:** Sí, por favor, ambos, porque en casa hay niños que todavía no usan bien los palitos.

**A:** Con gusto, así todos podrán comer cómodos. También incluimos servilletas en cantidad suficiente.

**B:** Qué amable. Una duda: ¿los recipientes se pueden meter al microondas?

**A:** Sí, son aptos para microondas, aunque recomendamos retirar la tapa antes de calentar la comida.

**B:** Entendido, gracias por avisarme, así evito cualquier accidente.

**A:** Y si algún día quiere hacer un pedido más grande, para una reunión o una celebración, lo ideal es llamarnos con anticipación para preparar todo con calma.

**B:** Buena idea, lo voy a tener en cuenta. Hay una celebración familiar más adelante y seguro necesitaremos algo así.

**A:** También puede guardar nuestro número en su teléfono, así la próxima vez la atendemos todavía más rápido.

**B:** Buena idea, lo guardo ahora mismo para no tener que buscarlo después.

**A:** Le comento que por el monto de su pedido no aplica ninguna promoción hoy, porque el descuento empieza desde noventa soles.

**B:** Está bien, no hay problema.

**A:** ¿Cuál es su dirección?

**B:** Calle Los Naranjos ciento cincuenta y seis, en Pueblo Libre, casa de portón verde.

**A:** Calle Los Naranjos ciento cincuenta y seis, Pueblo Libre. ¿Cómo pagará?

**B:** Con Yape, ahora mismo, si me envía el código.

**A:** Claro, se lo enviaremos por mensaje. El total es sesenta y ocho soles.

**B:** Sesenta y ocho soles, correcto. ¿Atienden hasta tarde?

**A:** Hasta las once de la noche. Repito su pedido: un chaufa familiar, un tallarín saltado mixto y un wantán frito, por sesenta y ocho soles.

**B:** Así es. ¿Cuánto demoran?

**A:** Aproximadamente treinta y cinco minutos.

**B:** Muchas gracias.

**A:** A usted, buen provecho.

> Nota para el validador: Correcto: 34 + 22 + 12 = 68. El pedido no llega a 90, así que no aplica Q1 (la vendedora lo menciona: trampa para el extractor de promoción).

---

## t2_02  (llamada)

- Palabras: 409 · duración estimada: ~3.2 min
- Trampas: AUTOCORRECCIÓN (2 sopas de wantán → 1). TOTAL INCORRECTO (dice 72, correcto 62: 'sesenta y dos' vs 'setenta y dos', parece error de ASR pero es del hablante porque lo repite). Dirección con dígitos. Promo 3x2.

**A:** Chifa Dragón Dorado, buenas noches, ¿qué desea pedir?

**B:** Buenas noches. Quiero dos arroces chaufa personales y dos sopas de wantán.

**A:** Anotado. ¿Algo más?

**B:** Sí, tres gaseosas personales. Ah, y perdón, sobre las sopas: mejor una sola sopa de wantán, no dos. Solo una persona la quiere.

**A:** Entendido, entonces dos chaufas personales, una sopa de wantán y tres gaseosas personales.

**B:** Correcto. ¿Las gaseosas son de sabores variados?

**A:** Sí, tenemos de cola, de naranja y de limón.

**B:** Dos de cola y una de naranja, por favor.

**A:** Listo. Los precios son: el chaufa personal, dieciocho soles; la sopa de wantán, dieciséis soles; y cada gaseosa personal, cinco soles. Además, hoy tenemos tres por dos en gaseosas personales, o sea que por tres paga solo dos.

**B:** Qué bien, entonces las tres gaseosas me salen al precio de dos.

**A:** Así es. ¿Cuál es su dirección de entrega?

**B:** Avenida Brasil mil doscientos diez, en Breña, al lado del banco.

**A:** Avenida Brasil mil doscientos diez, Breña. ¿Y cómo va a pagar?

**B:** En efectivo. ¿Me puede avisar cuando esté llegando?

**A:** Claro, el repartidor la llamará. El total sería setenta y dos soles.

**B:** ¿Setenta y dos soles? Bueno, está bien.

**A:** Sí, setenta y dos soles en total. Llegará en cuarenta minutos más o menos.

**B:** Perfecto. ¿Pueden enviar palitos chinos?

**A:** Con gusto, le ponemos palitos, servilletas y sobrecitos de sillao.

**B:** Una cosa más: mi vecina me dijo que su pedido anterior llegó rápido. ¿Cómo hacen para que no demore?

**A:** Tenemos varios repartidores por zona y preparamos el pedido apenas termina la llamada, así que sale de la cocina en pocos minutos.

**B:** Qué eficiente. Y si llueve, ¿también llega a tiempo?

**A:** Con lluvia puede demorar un poco más, pero le avisaremos si eso pasa, para que no se preocupe.

**B:** Gracias por la sinceridad, se agradece mucho.

**A:** A usted por su paciencia. Nos esforzamos para que el pedido llegue siempre en buen estado.

**B:** Otra pregunta: ¿ustedes preparan la comida en el momento o ya la tienen lista de antes?

**A:** La preparamos en el momento, apenas recibimos el pedido. Los ingredientes llegan frescos cada mañana y por eso el sabor es distinto al de un plato recalentado.

**B:** Muchas gracias. ¿La sopa de wantán viene caliente?

**A:** Sí, la enviamos en un envase térmico para que llegue bien caliente.

**B:** Excelente, gracias.

**A:** ¿Desea agregar un postre? Tenemos helado frito, recién hecho.

**B:** No, gracias, solo eso. Es una cena sencilla en casa.

**A:** Perfecto, entonces queda tal cual. Que lo disfruten.

**B:** Igualmente.

**A:** Gracias a usted. Buenas noches.

> Nota para el validador: Correcto: 2x18 + 16 + 3x5 = 67; promo 3x2 resta una gaseosa (5) = 62. La vendedora dice 72 y la cliente lo repite igual (error del HABLANTE). Ojo: 62 vs 72 es una confusión fonética plausible del ASR: sirve para probar tu regla de diagnóstico.

---

## t2_03  (llamada)

- Palabras: 413 · duración estimada: ~3.2 min
- Trampas: AUTOCORRECCIÓN (3 chaufas familiares → 2). Total CORRECTO. Recojo en tienda (sin dirección). Pago con tarjeta.

**A:** Chifa Dragón Dorado, buenas tardes, ¿en qué le ayudo?

**B:** Buenas tardes. Quiero hacer un pedido grande para una reunión familiar, y lo voy a recoger en la tienda.

**A:** Con gusto, dígame.

**B:** Quiero tres arroces chaufa familiares, un tallarín saltado y dos porciones de wantán frito. Y una jarra de limonada.

**A:** Perfecto.

**B:** Mmm, espera, tres chaufas familiares es demasiado. Mejor dos chaufas familiares. Lo demás está igual.

**A:** Entendido: dos chaufas familiares, un tallarín saltado, dos porciones de wantán frito y una jarra de limonada.

**B:** Exacto. ¿La limonada es con hielo?

**A:** Sí, y se la preparamos con el hielo aparte para que no se diluya.

**B:** Mejor aparte, gracias.

**A:** Los precios son: chaufa familiar, treinta y cuatro soles cada uno; tallarín saltado, veintidós soles; wantán frito, doce soles cada porción; y la jarra de limonada, catorce soles. Y hoy tenemos un descuento de quince soles en pedidos desde noventa soles.

**B:** Mi pedido califica, ¿verdad?

**A:** Sí. La suma es ciento veintiocho soles, menos quince, son ciento trece soles en total.

**B:** Ciento trece soles. Perfecto.

**A:** ¿A nombre de quién será el pedido?

**B:** A nombre de Milagros.

**A:** Milagros, listo. ¿Cómo pagará?

**B:** Con tarjeta, cuando lo recoja.

**A:** Perfecto. Estará listo en treinta minutos.

**B:** Gracias. ¿Hasta qué hora atienden?

**A:** Hasta las once de la noche.

**B:** Entonces paso en un rato. ¿Tienen estacionamiento?

**A:** Sí, hay espacio al costado del local, y si está lleno puede dejar el auto en la calle.

**B:** Genial, gracias. Una cosa más: ¿pueden poner las porciones de wantán en un envase aparte para que no se humedezcan?

**A:** Claro, las empacamos aparte con su salsa de tamarindo, así llegan bien crocantes.

**B:** Perfecto, muchas gracias.

**A:** Antes de despedirnos, ¿desea que le dejemos el contacto de la tienda, por si hay algún cambio?

**B:** Sí, por favor, para avisar si tengo algún retraso en llegar.

**A:** Claro. Nuestro teléfono es el mismo desde el que usted está llamando ahora.

**B:** Ah, entonces no hace falta, queda registrado en mi teléfono.

**A:** Exacto. Y si llega antes de la hora indicada, avísenos desde la puerta y lo atendemos primero.

**B:** Qué amable, así lo haré. Gracias por todo.

**A:** Si necesita que le guardemos el pedido en un lugar tibio mientras llega, no se preocupe, lo dejamos en la zona de entrega del local con su nombre.

**B:** Muchas gracias, qué detalle. Hoy el tráfico está pesado y no sé exactamente cuánto me voy a demorar en llegar.

**A:** Repito: dos chaufas familiares, un tallarín saltado, dos wantanes fritos y una limonada, ciento trece soles. La esperamos, Milagros.

**B:** Hasta luego.

> Nota para el validador: Correcto: 2x34 + 22 + 2x12 + 14 = 128; menos 15 = 113. Total dicho 113 (correcto).

---

## t2_04  (llamada)

- Palabras: 421 · duración estimada: ~3.3 min
- Trampas: TOTAL INCORRECTO (dice 76 = olvidó el tres por dos; correcto 71). Dirección con dígitos, interior y distrito. Cantidad 4 en promo 3x2.

**A:** Chifa Dragón Dorado, buenas tardes, ¿qué desea?

**B:** Hola, buenas tardes. Quiero pedir para mi casa, para delivery.

**A:** Claro, dígame su pedido.

**B:** Un arroz chaufa personal, un tallarín saltado, una sopa de wantán y cuatro gaseosas personales.

**A:** Perfecto. ¿Las gaseosas de qué sabor?

**B:** Dos de cola y dos de naranja.

**A:** Anotado. ¿Desea algo más?

**B:** No, con eso estamos bien. Es para el almuerzo con mis sobrinos.

**A:** Qué bien. Los precios son: chaufa personal, dieciocho soles; tallarín saltado, veintidós soles; sopa de wantán, dieciséis soles; y la gaseosa personal, cinco soles cada una. Hoy tenemos tres por dos en gaseosas personales.

**B:** Entonces con cuatro gaseosas, una me sale gratis, ¿no?

**A:** Así es, por cada tres paga dos, entonces en cuatro una es gratis.

**B:** ¿Y las gaseosas llegan frías?

**A:** Sí, salen de la refrigeradora y las enviamos en una bolsa aparte para que no se golpeen.

**B:** Perfecto.

**A:** ¿Quiere que le enviemos los palitos y los cubiertos en bolsas separadas?

**B:** Sí, por favor, porque mis sobrinos no usan palitos y prefieren tenedor.

**A:** Anotado. También podemos enviar los sobrecitos de sillao y de ají, por si alguien los desea.

**B:** Perfecto, mándelos todos. A mis sobrinos les encanta mezclar la salsa con toda la comida.

**A:** Qué lindo. Entonces los incluimos. Si hay algún ingrediente que alguien en la mesa no coma, avísenos para tener cuidado.

**B:** No hay ninguno, gracias, en mi casa comemos de todo.

**A:** Un detalle más: si alguien de la familia prefiere comida menos grasosa, la cocina puede prepararla con menos aceite, solo avíseme.

**B:** Qué amable. Mi hermana siempre pide eso, así que le diré que lo tienen. Gracias por avisarme.

**A:** Con eso ya estaría todo anotado. Si recuerda algo más, todavía estamos a tiempo de agregarlo al pedido.

**B:** Creo que no me falta nada, pero se lo agradezco, es usted muy atenta.

**A:** ¿Cuál es su dirección de entrega?

**B:** Jirón Lampa ciento ochenta y cinco, interior tres, en el Cercado de Lima.

**A:** Jirón Lampa ciento ochenta y cinco, interior tres, Cercado de Lima. ¿Cómo pagará?

**B:** En efectivo. ¿Tiene sencillo el repartidor? Voy a pagar con un billete de cien.

**A:** Sí, llevará vuelto. El total sería setenta y seis soles.

**B:** ¿Setenta y seis soles? Está bien.

**A:** Sí, setenta y seis soles. Su pedido llegará en cuarenta y cinco minutos.

**B:** Gracias. ¿El tallarín viene con verduras?

**A:** Sí, con verduras salteadas, cebolla china y pimiento.

**B:** Perfecto. ¿Y el chaufa lleva huevo?

**A:** Sí, lleva huevo, cebolla china y trocitos de pollo o cerdo, según prefiera.

**B:** De pollo, por favor.

**A:** Anotado, de pollo. Gracias por su pedido.

**B:** Gracias a usted.

> Nota para el validador: Correcto: 18 + 22 + 16 + 4x5 = 76; promo 3x2 con 4 gaseosas regala 1 (5) = 71. La vendedora dice 76 (no aplicó la promo) y lo repite.

---

## t2_05  (llamada)

- Palabras: 417 · duración estimada: ~3.3 min
- Trampas: AUTOCORRECCIÓN (2 tallarines → 3). TOTAL INCORRECTO (dice 148, correcto 143: la vendedora restó 10 en vez de 15; 'cuarenta y ocho' vs 'cuarenta y tres' es una confusión plausible de ASR). Dirección con dígitos y piso.

**A:** Chifa Dragón Dorado, buenas tardes, ¿cómo puedo ayudarle?

**B:** Buenas tardes, quiero hacer un pedido para el almuerzo de mi oficina, para delivery.

**A:** Claro, dígame.

**B:** Quiero dos arroces chaufa familiares, dos tallarines saltados y dos porciones de wantán frito.

**A:** Perfecto.

**B:** Pensándolo bien, mejor tres tallarines saltados, porque somos nueve personas y los chaufas no alcanzan para todos.

**A:** Entendido, dos chaufas familiares, tres tallarines saltados y dos porciones de wantán frito.

**B:** Así es. ¿Pueden hacer los tallarines sin picante?

**A:** Sin problema, los anotamos sin ají.

**B:** Una consulta: ¿el wantán frito viene caliente o hay que recalentarlo?

**A:** Sale recién hecho, pero si el reparto demora, se puede pasar unos minutos por la sartén para que quede crocante.

**B:** Entendido. Y los tallarines, ¿vienen con carne o con pollo?

**A:** Si no nos dice nada, los preparamos mixtos, con carne y pollo.

**B:** Gracias.

**A:** Los precios son: chaufa familiar, treinta y cuatro soles cada uno; tallarín saltado, veintidós soles cada uno; y la porción de wantán frito, doce soles. Hoy tenemos descuento de quince soles en pedidos desde noventa soles, y su pedido califica.

**B:** Qué bien.

**A:** ¿Cuál es su dirección?

**B:** Avenida La Marina tres mil cuatrocientos veinte, en Los Olivos, edificio de oficinas, piso cuatro.

**A:** Avenida La Marina tres mil cuatrocientos veinte, Los Olivos, piso cuatro. ¿Cómo desea pagar?

**B:** Con Yape.

**A:** Perfecto, le enviaremos el código. El total sería ciento cuarenta y ocho soles.

**B:** ¿Ciento cuarenta y ocho? De acuerdo.

**A:** Sí, ciento cuarenta y ocho soles. Llegará en cincuenta minutos, más o menos.

**B:** ¿Se puede entregar antes de las doce? Tenemos una reunión.

**A:** Haremos lo posible, lo ponemos como prioridad.

**B:** ¿Y pueden enviar platos descartables para todos?

**A:** Claro, le enviamos platos, cubiertos y servilletas para nueve personas.

**B:** Una cosa más: en el edificio hay vigilante en la entrada. ¿El repartidor puede avisar desde la portería?

**A:** Claro, le pedimos que pregunte por usted en la portería y que la llame por teléfono para que baje a recoger el pedido.

**B:** Perfecto, porque la oficina queda dentro de un edificio grande y a veces no se escucha el timbre.

**A:** Entendido. Lo anotamos en la hoja del pedido para que no haya confusión.

**B:** Y si llega antes de lo previsto, ¿puede esperar abajo unos minutos?

**A:** Sí, sin problema. Esperará en la entrada hasta que usted baje.

**B:** Otra cosa: como somos varios, ¿pueden mandar todo bien separado por bolsas para repartirlo más fácil?

**A:** Claro, separamos todo en bolsas y marcamos cada una por contenido, para que se repartan fácil sin abrir todas.

**B:** Muchas gracias.

**A:** Gracias a usted, buenas tardes.

> Nota para el validador: Correcto: 2x34 + 3x22 + 2x12 = 158; menos 15 = 143. La vendedora dice 148 y la cliente lo repite (error del HABLANTE).

---
