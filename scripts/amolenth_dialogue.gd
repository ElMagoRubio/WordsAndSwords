extends Node2D

@onready var entrada_texto = $HUD/CajaTexto/Texto
@onready var boton_hablar = $HUD/Hablar
@onready var boton_enviar_texto = $HUD/Enviar
@onready var boton_retar = $HUD/Retar
@onready var boton_rendirse = $HUD/Rendirse
@onready var procesando_texto = false
@onready var http_request = $HTTPRequest

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
	
	enviar_texto_a_api(texto_envio)


func enviar_texto_a_api(texto):
	var url = "https://api.tuapi.com/endpoint" # Cambia esto por la URL de tu API
	var json_data = {
	"texto": texto
	}
	var json = JSON.new()
	var json_string = json.print(json_data)
	
	var headers = ["Content-Type: application/json"]
	
	var error = http_request.request(url, headers, false, HTTPClient.METHOD_POST, json_string)
	if error != OK:
		print("Error al enviar la solicitud: %s" % error)


func _on_http_request_request_completed(result, response_code, headers, body):
	if response_code == 200:
		var json = JSON.new()
		var response_json = json.parse(body.get_string_from_utf8())
		if response_json.error == OK:
			var response_data = response_json.result
			print("Respuesta de la API: %s" % response_data)
			entrada_texto.text = response_data
			boton_hablar.disabled = false
			boton_retar.disabled = false
			boton_rendirse.disabled = false
		else:
			print("Error en la respuesta de la API: %s" % response_json.error_string)
	else:
		print("Error en la solicitud HTTP: %s" % response_code)
