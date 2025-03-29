extends Node2D

@onready var entrada_texto = $HUD/CajaTexto/Texto
@onready var boton_hablar = $HUD/Hablar
@onready var boton_enviar_texto = $HUD/Enviar
@onready var boton_retar = $HUD/Retar
@onready var boton_rendirse = $HUD/Rendirse
@onready var procesando_texto = false

func _ready():
	entrada_texto.scroll_horizontal = true
	boton_hablar.visible = true
	boton_enviar_texto.visible = false

func _process(_delta):
	if (boton_enviar_texto.visible and entrada_texto.text != ""):
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
		entrada_texto.placeholder_text = "Escriba aquí"
		entrada_texto.grab_focus()
		entrada_texto.caret_blink = true


func _on_enviar_pressed():
	boton_hablar.visible = true
	boton_enviar_texto.visible = false
	var texto_envio = entrada_texto.text
	entrada_texto.text = "..."
	boton_hablar.disabled = true
	boton_retar.disabled = true
	boton_rendirse.disabled = true
	entrada_texto.editable = false
	
	enviar_texto_a_script(texto_envio)


func enviar_texto_a_script(texto):
	print("Iniciando generación de texto. Prompt: " + texto)
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
		entrada_texto.text = response
	else:
		print("Error al ejecutar el script")
		entrada_texto.text = "Error al procesar"
	
	#Habilitar botones tras hablar
	boton_hablar.disabled = false
	boton_retar.disabled = false
	boton_rendirse.disabled = false
