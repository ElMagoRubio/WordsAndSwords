extends Node2D

const python_cmd = "python"
const HOST = "127.0.0.1"
const PORT = 5005

@onready var peer = StreamPeerTCP.new()

@onready var caja_texto_1 = $HUD/CajaTexto1
@onready var entrada_texto_1 = $HUD/CajaTexto1/Texto
@onready var caja_texto_2 = $HUD/CajaTexto2
@onready var entrada_texto_2 = $HUD/CajaTexto2/Texto
@onready var caja_texto_3 = $HUD/CajaTexto3
@onready var entrada_texto_3 = $HUD/CajaTexto3/Texto
@onready var siguiente_escena = $HUD/SiguienteEscena

@onready var boton_hablar = $HUD/Hablar
@onready var boton_enviar_texto = $HUD/Enviar
@onready var boton_retar = $HUD/Retar
@onready var boton_rendirse = $HUD/Rendirse


@onready var flag_path = ProjectSettings.globalize_path("res://server/server_ready.flag")
@onready var next_scene_path = ""

@onready var procesando_texto = false
@onready var borrando_prompt = false
@onready var respuesta_generada = false
@onready var dev_mode = false
@onready var servidor_abierto = false


func _ready():
	$HUD/NombrePJ.text = Global.nombre_jugador
	$PJ.texture = load(Global.rutas_imagenes[Global.pj_jugador])
	entrada_texto_1.placeholder_text = "Cargando servidor..."
	entrada_texto_1.editable = false
	entrada_texto_1.scroll_horizontal = true
	entrada_texto_2.placeholder_text = "Cargando servidor..."
	entrada_texto_2.editable = false
	entrada_texto_2.scroll_horizontal = true
	entrada_texto_3.placeholder_text = "Cargando servidor..."
	entrada_texto_3.editable = false
	entrada_texto_3.scroll_horizontal = true
	boton_hablar.visible = true
	boton_hablar.disabled = true
	boton_enviar_texto.visible = false
	
	if !FileAccess.file_exists(flag_path):
		iniciar_server()
		var i = 0
		while !FileAccess.file_exists(flag_path):
			i += 1
			print("Esperando al servidor (",i,")...")
			await get_tree().create_timer(1).timeout
	
	servidor_abierto = true
	print("Confirmado inicio del servidor")
	
	conexion_server()
	
	boton_hablar.disabled = false
	entrada_texto_1.editable = true
	entrada_texto_1.placeholder_text = "Escriba aquí..."
	entrada_texto_2.editable = true
	entrada_texto_2.placeholder_text = "Escriba aquí..."
	entrada_texto_3.editable = true
	entrada_texto_3.placeholder_text = "Escriba aquí..."


func _process(_delta):
	if (boton_enviar_texto.visible and entrada_texto_1.text != ""):
		boton_enviar_texto.disabled = false
	else:
		boton_enviar_texto.disabled = true
	
	if servidor_abierto:
		if !FileAccess.file_exists(flag_path):
			servidor_abierto = false
			print("SERVIDOR CERRADO")
	
	if Input.is_action_just_pressed("ui_accept") and next_scene_path != "":
		get_tree().change_scene_to_file(next_scene_path)


func _exit_tree():
	cerrar_server()


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		cerrar_server()
		get_tree().quit()


func _on_retar_pressed():
	get_tree().change_scene_to_file("res://scenes/escenario.tscn")
	

func _on_rendirse_pressed():
	pass # Replace with function body.


func _on_hablar_pressed():
	_on_texto_focus_entered()


func _on_texto_focus_entered():
	if (boton_retar.disabled == false):
		boton_hablar.visible = false
		boton_enviar_texto.visible = true
		boton_enviar_texto.disabled = true
		entrada_texto_1.placeholder_text = "Escriba aquí"
		entrada_texto_1.grab_focus()
		entrada_texto_1.caret_blink = true
		if (dev_mode):
			entrada_texto_2.placeholder_text = "Escriba aquí"
			entrada_texto_2.caret_blink = true
			entrada_texto_3.placeholder_text = "Escriba aquí"
			entrada_texto_3.caret_blink = true
	
	if !procesando_texto:
		respuesta_generada = false
		entrada_texto_1.text = ""


func _on_enviar_pressed():
	boton_hablar.visible = true
	boton_enviar_texto.visible = false
	var texto_envio = entrada_texto_1.text
	boton_hablar.disabled = true
	boton_retar.disabled = true
	boton_rendirse.disabled = true
	entrada_texto_1.editable = false
	procesando_texto = true
	var request = {
		"code": "GENERATE",
		"text": texto_envio,
		"model": "flan-t5-finetuned_v1"
	}
	if (dev_mode):
		entrada_texto_2.text = "..."
		entrada_texto_3.text = "..."
	
	borrar_prompt()
	
	var response = await enviar_request(request)
	respuesta_generada = true
	
	var json = JSON.new()
	var err = json.parse(response)

	if err == OK:
		var result = json.get_data()
		print("Respuesta del modelo: ", result["response"])
		print("Nivel de emoción: ", result["emotion_level"])
		print("Acción: ", result["action"])
		await mostrar_respuesta(result["response"])
		
		if (result["action"] == "retar"):
			siguiente_escena.visible = true
			next_scene_path = ProjectSettings.globalize_path("res://scenes/escenario.tscn")
		
		elif(result["action"] == "rendirse"):
			siguiente_escena.visible = true
			next_scene_path = ProjectSettings.globalize_path("res://scenes/escena_rendicion.tscn")
		
	else:
		print("Error al parsear la respuesta JSON: ", err)
		entrada_texto_1.text = "Error al procesar respuesta del servidor."
	
	boton_hablar.disabled = false
	boton_retar.disabled = false
	boton_rendirse.disabled = false
	entrada_texto_1.editable = true


func _on_dev_mode_toggled():
	if (!dev_mode):
		print("Modo desarrollador: ACTIVO")
		dev_mode = true
		boton_rendirse.visible = false
		caja_texto_2.visible = true
		entrada_texto_2.editable = true
		caja_texto_3.visible = true
		entrada_texto_3.editable = true
	else:
		print("Modo desarrollador: INACTIVO")
		dev_mode = false
		boton_rendirse.visible = true
		caja_texto_2.visible = false
		entrada_texto_2.editable = false
		caja_texto_3.visible = false
		entrada_texto_3.editable = false


func _on_texto_text_changed():
	if (dev_mode):
		entrada_texto_2.text = entrada_texto_1.text
		entrada_texto_3.text = entrada_texto_1.text


func iniciar_server():
	print("Iniciando servidor")
	var script_path = ProjectSettings.globalize_path("res://server/server.py")
	print(script_path)
	var args = [script_path, Global.nombre_jugador]
	print(python_cmd, " ",script_path, " ", args)
	var exit_code = OS.create_process(python_cmd, args, false)
	print(exit_code)
	
	if exit_code:
		print("Iniciando servidor. Esperando confirmación de carga...")
		
	else:
		push_error("No se pudo iniciar el servidor")


func cerrar_server():
	print("Cerrando servidor...")
	
	var request = { "code": "CLOSE" }
	var exit_code = await enviar_request(request)
	print (exit_code)
	
	await get_tree().create_timer(1).timeout
	
	if exit_code == OK:
		print("Servidor cerrado.")


func conexion_server() -> String:
	var salida = ""
	if await enviar_request({"code": "PING"}) != "PONG":
		print("Conectando al servidor...")
		var err = peer.connect_to_host(HOST, PORT)
		if err != OK:
			return "[ERROR] No se pudo conectar al servidor."
		
		var timeout = 0.0
		while peer.get_status() == StreamPeerTCP.STATUS_CONNECTING and timeout < 10.0:
			print("Intentando conectar (", timeout,")")
			await get_tree().create_timer(0.1).timeout
			peer.poll()
			timeout += 0.1
		
		peer.poll()
		
		if peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
			if timeout >= 10.0:
				salida += "Tiempo de espera agotado.\n"
			salida += "Conexión fallida."
		else:
			salida += ("Conexión establecida.")
	else: 
		salida = "Conexión establecida"
	return salida


func enviar_request(request: Dictionary) -> String:
	print("Enviando petición: \n", request)
	if peer.get_status() != StreamPeerTCP.STATUS_CONNECTED:
		print("[ERROR]: Servidor no conectado")
		return "ERROR"
	
	var data = JSON.stringify(request).to_utf8_buffer()
	var err = peer.put_data(data)
	if err != OK:
		print("[ERROR]: Envío de datos erróneo")
		return "ERROR: Envío de datos erróneo"
	
	# Esperar una respuesta durante hasta 2 segundos
	var timeout = 15.0
	var time_elapsed = 0.0
	var interval = 0.1
	
	while true:
		await get_tree().create_timer(interval).timeout
		peer.poll()
		time_elapsed += interval
		if peer.get_available_bytes() > 0:
			var response = peer.get_utf8_string(peer.get_available_bytes())
			print("RESPUESTA OBTENIDA: \n", response)
			return response
	
	print("[ERROR]: Tiempo de espera agotado")
	return "ERROR: Tiempo de espera agotado"


func mostrar_respuesta(response: String):
	while borrando_prompt == true:
		await get_tree().create_timer(1).timeout
	
	entrada_texto_1.text = ""
	var counter_letra = 0
	while entrada_texto_1.text != response:
		entrada_texto_1.text += response[counter_letra]
		counter_letra += 1
		await get_tree().create_timer(0.1).timeout
	
	procesando_texto = false


func borrar_prompt():
	borrando_prompt = true
	var letra_final = entrada_texto_1.text.length() -1
	while entrada_texto_1.text != "" and letra_final >= 0:
		await get_tree().create_timer(0.1).timeout
		entrada_texto_1.text[letra_final] = ""
		letra_final -= 1
	entrada_texto_1.text = "."
	while !respuesta_generada:
		await get_tree().create_timer(0.5).timeout
		if (entrada_texto_1.text == "..."):
			entrada_texto_1.text = ""
		entrada_texto_1.text += "."
	borrando_prompt = false
