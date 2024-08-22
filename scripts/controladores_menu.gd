extends Control

@onready var menuOpciones = $MenuOpciones
@onready var menuAudio = $MenuAudio
@onready var menuVideo = $MenuVideo
@onready var headerText = $TextPausa


func _ready():
	menuOpciones.visible = true
	headerText.text = "PAUSA"
	menuAudio.visible = false
	menuVideo.visible = false


func _on_boton_audio_pressed():
	menuOpciones.visible = false
	headerText.text = "AUDIO"
	menuAudio.visible = true
	menuVideo.visible = false


func _on_boton_resolucion_pressed():
	menuOpciones.visible = false
	headerText.text = "RESOLUCION"
	menuAudio.visible = false
	menuVideo.visible = true


func _on_boton_salir_pressed():
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_boton_volver_pressed():
	menuOpciones.visible = true
	headerText.text = "PAUSA"
	menuAudio.visible = false
	menuVideo.visible = false


func _on_ajustes_pressed():
	menuOpciones.visible = true
	headerText.text = "PAUSA"
	menuAudio.visible = false
	menuVideo.visible = false


func _on_boton_reanudar_pressed():
	menuOpciones.visible = true
	headerText.text = "PAUSA"
	menuAudio.visible = false
	menuVideo.visible = false


func _on_fullscreen_pressed():
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_MAXIMIZED:
		$MenuVideo/HBoxContainer2/Borderless.set_pressed_no_signal(false)
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_MAXIMIZED)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)


func _on_borderless_pressed():
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN:
		$MenuVideo/HBoxContainer/Fullscreen.set_pressed_no_signal(false)
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN)
	else:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)

func _on_v_sync_pressed():
	if $MenuVideo/HBoxContainer2/Borderless.is_pressed:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	else:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
