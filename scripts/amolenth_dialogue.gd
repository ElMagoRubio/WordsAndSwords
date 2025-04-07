extends Node2D

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
	entrada_texto_1.scroll_horizontal = true
	entrada_texto_2.scroll_horizontal = true
	entrada_texto_3.scroll_horizontal = true
	boton_hablar.visible = true
	boton_enviar_texto.visible = false
	

func _process(_delta):
	if (boton_enviar_texto.visible and entrada_texto_1.text != ""):
		boton_enviar_texto.disabled = false
	else:
		boton_enviar_texto.disabled = true


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
	var python_cmd = "python"
	var script_path = "res://language_models/text_generation_flant5.py"
	var global_path = ProjectSettings.globalize_path(script_path)
	var args = [global_path, texto]
	var output = []
	
	print(OS.execute(python_cmd, args, output, true, true))
	var exit_code = OS.execute(python_cmd, args, output, true, true)
	
	if exit_code == 0:
		var response = output[0].strip_edges() # Limpia espacios innecesarios
		print("Respuesta del script: ", response)
		entrada_texto_1.text = response
	else:
		print("Error al ejecutar el script")
		entrada_texto_1.text = "Error al procesar"
	
	if (dev_mode):
		print("Iniciando generación de texto 2. Prompt: " + texto)
		python_cmd = "python"
		script_path = "res://language_models/text_generation_smol.py"
		global_path = ProjectSettings.globalize_path(script_path)
		args = [global_path, texto]
		output = []
		
		print(OS.execute(python_cmd, args, output, true, true))
		exit_code = OS.execute(python_cmd, args, output, true, true)
		
		if exit_code == 0:
			var response = output[0].strip_edges() # Limpia espacios innecesarios
			print("Respuesta del script: ", response)
			entrada_texto_2.text = response
		else:
			print("Error al ejecutar el script")
			entrada_texto_2.text = "Error al procesar"
		
		print("Iniciando generación de texto 3. Prompt: " + texto)
		python_cmd = "python"
		script_path = "res://language_models/text_generation_phi.py"
		global_path = ProjectSettings.globalize_path(script_path)
		args = [global_path, texto]
		output = []
		
		print(OS.execute(python_cmd, args, output, true, true))
		exit_code = OS.execute(python_cmd, args, output, true, true)
		
		if exit_code == 0:
			var response = output[0].strip_edges() # Limpia espacios innecesarios
			print("Respuesta del script: ", response)
			entrada_texto_3.text = response
		else:
			print("Error al ejecutar el script")
			entrada_texto_3.text = "Error al procesar"
	
	#Habilitar botones tras hablar
	boton_hablar.disabled = false
	boton_retar.disabled = false
	boton_rendirse.disabled = false
	entrada_texto_1.editable = true


func _on_dev_mode_toggled(button_down):
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
