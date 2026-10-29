"""Relleno conversacional (SET B) para llevar cada clip a ~3.3-3.7 min.

Alinea el corpus con lo que pide el caso: 4-5 clips de 2-4 min y ~16-20 min de audio por tarea.
Regla: el relleno NO menciona valores de ningún campo (puestos, años, tecnologías, salarios,
disponibilidad, inglés / productos, precios, cantidades, promos, direcciones, pagos), para que
el ground truth no cambie.

Formato:  id_clip -> (linea_ancla, [(hablante, texto), ...])
El bloque se inserta justo DESPUÉS de la línea ancla (igualdad exacta, o prefijo si es larga).
"""

RELLENO = {
    # ---------------------------------------------------------------- T1 (A entrevista, B candidata)
    "t1_01": ("Las tomo como información.", [
        ("A", "Cuéntame cómo investigas lo que necesitan las personas que van a usar un producto."),
        ("B", "Empiezo conversando con ellas, sin mostrarles nada todavía. Les pregunto cómo resuelven hoy ese problema y dónde se frustran. Con esas historias dibujo un primer boceto y recién ahí lo pruebo."),
        ("A", "¿Y qué haces cuando lo que piden los clientes choca con lo que ven los usuarios?"),
        ("B", "Llevo ejemplos reales a la mesa. Un comentario de un usuario de carne y hueso pesa más que mi opinión. Casi siempre, el cliente cambia de idea cuando escucha cómo se confunde la gente."),
        ("A", "¿Qué haces cuando un diseño tuyo no funciona en las pruebas?"),
        ("B", "Me alegro de haberlo descubierto antes de que se publique. Anoto qué falló, rehago esa parte y lo vuelvo a probar. Aprendí que el primer diseño casi nunca es el definitivo."),
    ]),
    "t1_02": ("Primero comparo contra el mes anterior", [
        ("A", "Cuéntame cómo explicas los resultados financieros a personas que no son del área."),
        ("B", "Evito los términos técnicos y uso comparaciones cotidianas. Por ejemplo, explico el flujo de caja como el dinero que realmente hay en la cuenta al cierre, aunque todavía falte cobrar algunas facturas."),
        ("A", "¿Qué haces cuando la gerencia te pide una cifra que no se puede sostener con los datos?"),
        ("B", "Les explico con calma qué se puede afirmar y qué no. Prefiero decir que no tengo ese dato todavía y ofrecer una estimación clara, antes que dar una cifra que después tenga que corregir."),
        ("A", "¿Cómo te mantienes al día con los cambios en las normas?"),
        ("B", "Leo los boletines del colegio profesional y converso con colegas de otras empresas. Además, anoto en un cuaderno compartido los cambios que afectan a mi equipo, para que nadie los olvide."),
    ]),
    "t1_03": ("Primero intento reproducirlo en un ejemplo pequeño", [
        ("A", "¿Cómo te aseguras de que lo que construyes sea fácil de usar para todas las personas?"),
        ("B", "Pruebo con el teclado, sin usar el ratón, y reviso que los textos se lean bien con letras grandes. También pido a una amiga con poca vista que lo pruebe y me cuente dónde se pierde."),
        ("A", "Qué interesante. ¿Qué valoras en la revisión del trabajo de otras personas?"),
        ("B", "Que se comente con respeto y con una razón. Si me piden que cambie algo, me gusta entender por qué. Y cuando reviso a otras, intento comenzar por lo que me gustó antes de señalar mejoras."),
        ("A", "¿Cómo imaginas tu crecimiento dentro de un tiempo?"),
        ("B", "Me gustaría ser alguien en quien el equipo confíe para tareas difíciles, y también ayudar a las personas que recién empiezan. Cuando yo llegué, me ayudaron mucho, y quiero devolverlo."),
    ]),
    "t1_04": ("Me gustan las metas mensuales", [
        ("A", "Cuéntame cómo trabajas con diseñadoras y redactoras cuando tienen ideas distintas a las tuyas."),
        ("B", "Les pido que me expliquen su idea completa y cuál es el objetivo detrás. Muchas veces coincidimos en lo que queremos lograr y solo cambia el camino, así que probamos ambos y vemos qué funciona mejor."),
        ("A", "¿Qué haces cuando una campaña no da el resultado que esperabas?"),
        ("B", "Dejo pasar un poco de tiempo para no reaccionar con prisa y luego reviso qué cambió. A veces fue el mensaje, a veces el momento. Lo importante es aprender algo y compartirlo con el equipo."),
        ("A", "¿Cómo te gusta que te den seguimiento en tu trabajo?"),
        ("B", "Con reuniones cortas y frecuentes, y con comentarios concretos. Si me dicen qué salió bien y qué ajustar, puedo corregir rápido sin esperar a una evaluación larga."),
    ]),
    "t1_05": ("Con paciencia y sin jerga.", [
        ("A", "¿Cómo te aseguras de que un modelo no perjudique injustamente a ciertas personas?"),
        ("B", "Reviso cómo se comporta con distintos grupos antes de llevarlo a producción. Si veo diferencias que no se explican por el riesgo real, vuelvo a revisar las variables y consulto con el área legal."),
        ("A", "Importante. ¿Qué haces cuando los datos que tienes no son suficientes?"),
        ("B", "Lo digo desde el inicio y propongo recoger más información o usar un modelo más sencillo. Prefiero un resultado modesto pero honesto que uno impresionante que no se sostiene."),
        ("A", "¿Cómo compartes lo que aprendes con el resto del equipo?"),
        ("B", "Escribo notas cortas después de cada proyecto con lo que funcionó y lo que no, y organizo una charla informal para que cualquiera pueda preguntar. Así no se pierde lo aprendido."),
    ]),

    # ---------------------------------------------------------------- T2 (A vende, B compra)
    "t2_01": ("Gracias.", [
        ("A", "Si lo desea, también podemos enviar cucharas y tenedores descartables, además de los palitos."),
        ("B", "Sí, por favor, ambos, porque en casa hay niños que todavía no usan bien los palitos."),
        ("A", "Con gusto, así todos podrán comer cómodos. También incluimos servilletas en cantidad suficiente."),
        ("B", "Qué amable. Una duda: ¿los recipientes se pueden meter al microondas?"),
        ("A", "Sí, son aptos para microondas, aunque recomendamos retirar la tapa antes de calentar la comida."),
        ("B", "Entendido, gracias por avisarme, así evito cualquier accidente."),
        ("A", "Y si algún día quiere hacer un pedido más grande, para una reunión o una celebración, lo ideal es llamarnos con anticipación para preparar todo con calma."),
        ("B", "Buena idea, lo voy a tener en cuenta. Hay una celebración familiar más adelante y seguro necesitaremos algo así."),
        ("A", "También puede guardar nuestro número en su teléfono, así la próxima vez la atendemos todavía más rápido."),
        ("B", "Buena idea, lo guardo ahora mismo para no tener que buscarlo después."),
    ]),
    "t2_02": ("Con gusto, le ponemos palitos, servilletas y sobrecitos de sillao.", [
        ("B", "Una cosa más: mi vecina me dijo que su pedido anterior llegó rápido. ¿Cómo hacen para que no demore?"),
        ("A", "Tenemos varios repartidores por zona y preparamos el pedido apenas termina la llamada, así que sale de la cocina en pocos minutos."),
        ("B", "Qué eficiente. Y si llueve, ¿también llega a tiempo?"),
        ("A", "Con lluvia puede demorar un poco más, pero le avisaremos si eso pasa, para que no se preocupe."),
        ("B", "Gracias por la sinceridad, se agradece mucho."),
        ("A", "A usted por su paciencia. Nos esforzamos para que el pedido llegue siempre en buen estado."),
        ("B", "Otra pregunta: ¿ustedes preparan la comida en el momento o ya la tienen lista de antes?"),
        ("A", "La preparamos en el momento, apenas recibimos el pedido. Los ingredientes llegan frescos cada mañana y por eso el sabor es distinto al de un plato recalentado."),
    ]),
    "t2_03": ("Perfecto, muchas gracias.", [
        ("A", "Antes de despedirnos, ¿desea que le dejemos el contacto de la tienda, por si hay algún cambio?"),
        ("B", "Sí, por favor, para avisar si tengo algún retraso en llegar."),
        ("A", "Claro. Nuestro teléfono es el mismo desde el que usted está llamando ahora."),
        ("B", "Ah, entonces no hace falta, queda registrado en mi teléfono."),
        ("A", "Exacto. Y si llega antes de la hora indicada, avísenos desde la puerta y lo atendemos primero."),
        ("B", "Qué amable, así lo haré. Gracias por todo."),
        ("A", "Si necesita que le guardemos el pedido en un lugar tibio mientras llega, no se preocupe, lo dejamos en la zona de entrega del local con su nombre."),
        ("B", "Muchas gracias, qué detalle. Hoy el tráfico está pesado y no sé exactamente cuánto me voy a demorar en llegar."),
    ]),
    "t2_04": ("Perfecto.", [
        ("A", "¿Quiere que le enviemos los palitos y los cubiertos en bolsas separadas?"),
        ("B", "Sí, por favor, porque mis sobrinos no usan palitos y prefieren tenedor."),
        ("A", "Anotado. También podemos enviar los sobrecitos de sillao y de ají, por si alguien los desea."),
        ("B", "Perfecto, mándelos todos. A mis sobrinos les encanta mezclar la salsa con toda la comida."),
        ("A", "Qué lindo. Entonces los incluimos. Si hay algún ingrediente que alguien en la mesa no coma, avísenos para tener cuidado."),
        ("B", "No hay ninguno, gracias, en mi casa comemos de todo."),
        ("A", "Un detalle más: si alguien de la familia prefiere comida menos grasosa, la cocina puede prepararla con menos aceite, solo avíseme."),
        ("B", "Qué amable. Mi hermana siempre pide eso, así que le diré que lo tienen. Gracias por avisarme."),
        ("A", "Con eso ya estaría todo anotado. Si recuerda algo más, todavía estamos a tiempo de agregarlo al pedido."),
        ("B", "Creo que no me falta nada, pero se lo agradezco, es usted muy atenta."),
    ]),
    "t2_05": ("Claro, le enviamos platos, cubiertos y servilletas para nueve personas.", [
        ("B", "Una cosa más: en el edificio hay vigilante en la entrada. ¿El repartidor puede avisar desde la portería?"),
        ("A", "Claro, le pedimos que pregunte por usted en la portería y que la llame por teléfono para que baje a recoger el pedido."),
        ("B", "Perfecto, porque la oficina queda dentro de un edificio grande y a veces no se escucha el timbre."),
        ("A", "Entendido. Lo anotamos en la hoja del pedido para que no haya confusión."),
        ("B", "Y si llega antes de lo previsto, ¿puede esperar abajo unos minutos?"),
        ("A", "Sí, sin problema. Esperará en la entrada hasta que usted baje."),
        ("B", "Otra cosa: como somos varios, ¿pueden mandar todo bien separado por bolsas para repartirlo más fácil?"),
        ("A", "Claro, separamos todo en bolsas y marcamos cada una por contenido, para que se repartan fácil sin abrir todas."),
    ]),
}
