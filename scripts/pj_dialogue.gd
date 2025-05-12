extends Node2D

@onready var python_cmd = "python"

@onready var caja_texto_1 = $HUD/CajaTexto1
@onready var entrada_texto_1 = $HUD/CajaTexto1/Texto
@onready var caja_texto_2 = $HUD/CajaTexto2
@onready var entrada_texto_2 = $HUD/CajaTexto2/Texto
@onready var caja_texto_3 = $HUD/CajaTexto3
@onready var entrada_texto_3 = $HUD/CajaTexto3/Texto

@onready var boton_hablar = $HUD/Hablar
@onready var boton_enviar_texto = $HUD/Enviar
@onready var boton_retar = $HUD/Retar
@onready var boton_rendirse = $HUD/Rendirse

@onready var procesando_texto = false
@onready var dev_mode = false

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
	
	iniciar_server()
	
	var flag_path = ProjectSettings.globalize_path("res://server/server_ready.flag")
	var i = 0
	while !FileAccess.file_exists(flag_path):
		i += 1
		print("Esperando al servidor (",i,")...")
		await get_tree().create_timer(1).timeout
		
	DirAccess.remove_absolute(flag_path)
	print("Confirmado inicio del servidor, esperando peticiones")
	
	
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


func _on_enviar_pressed():
	boton_hablar.visible = true
	boton_enviar_texto.visible = false
	var texto_envio = entrada_texto_1.text
	boton_hablar.disabled = true
	boton_retar.disabled = true
	boton_rendirse.disabled = true
	entrada_texto_1.text = "..."
	entrada_texto_1.editable = false
	if (dev_mode):
		entrada_texto_2.text = "..."
		entrada_texto_3.text = "..."
	
	enviar_texto_a_script(texto_envio)


func enviar_texto_a_script(texto):
	print("Iniciando generación de texto 1. Prompt: " + texto)
	var script_path = "res://server/request.py"
	var global_path = ProjectSettings.globalize_path(script_path)
	var args = [global_path, 0, texto]
	var output = []
	var exit_code = OS.execute(python_cmd, args, output, true, true)
	
	print("Salida del servidor: ", exit_code)
	
	if exit_code == 0:
		var raw_json = "".join(output).strip_edges()
		var json = JSON.new()
		var parse_result = json.parse(raw_json)
		
		if parse_result == OK:
			var result = json.get_data()
			print("Respuesta del modelo: ", result["response"])
			print("Nivel de emoción: ", result["emotion_level"])
			print("Acción: ", result["action"])
			
			entrada_texto_1.text = result["response"]
			
			# Aquí podrías usar el valor de result["action"] si necesitas reaccionar
			# Por ejemplo:
			# if result["action"] == "rendirse":
			#     mostrar_victoria()
		else:
			print("Error al parsear JSON: ", parse_result)
			entrada_texto_1.text = "Error al procesar respuesta"
		
	else:
		print("Error al ejecutar el script")
		entrada_texto_1.text = "Error al procesar respuesta"
	
	#Habilitar botones tras hablar
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
	var script_path = ProjectSettings.globalize_path("res://server/close_server_request.py")
	var exit_code = OS.execute(python_cmd, [script_path])
	
	if exit_code == OK:
		print("Servidor cerrado.")
