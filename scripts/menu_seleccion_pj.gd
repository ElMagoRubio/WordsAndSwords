extends Node2D

@onready var btn_ant = $TablaLarga/Control/ButtonPjAnterior
@onready var btn_sig = $TablaLarga/Control/ButtonPjSiguiente
@onready var sprite_pj = $TablaLarga/Control/PJSeleccionado
@onready var nombre_pj = $NombrePJ
@onready var regiones_normal = [
	Rect2(103, 1, 21, 46),  # Amolenth
	Rect2(32, 1, 22, 46),   # Baspiek
	Rect2(55, 1, 23, 46),   # Easttain
	Rect2(79, 1, 24, 46),   # Galeth
	Rect2(0, 1, 31, 46)     # Vilgard
]

@onready var regiones_hover = [
	Rect2(103, 67, 21, 46),  # Amolenth
	Rect2(32, 67, 22, 46),   # Baspiek
	Rect2(55, 67, 23, 46),   # Easttain
	Rect2(79, 67, 24, 46),   # Galeth
	Rect2(0, 67, 31, 46)     # Vilgard
]

@onready var regiones_pressed = [
	Rect2(103, 131, 21, 46),  # Amolenth
	Rect2(32, 131, 23, 46),   # Baspiek
	Rect2(55, 131, 23, 46),   # Easttain
	Rect2(79, 131, 24, 46),   # Galeth
	Rect2(0, 131, 31, 46)     # Vilgard
]

@onready var regiones = [regiones_normal, regiones_hover, regiones_pressed]

func _ready():
	actualizar_pj(0)

func _on_button_pj_anterior_pressed():
	Global.pj_jugador -= 1
	if (Global.pj_jugador < 0):
		Global.pj_jugador = regiones[0].size()-1
	actualizar_pj(0)


func _on_button_pj_siguiente_pressed():
	Global.pj_jugador = (Global.pj_jugador + 1) % regiones[0].size()
	if (Global.pj_jugador < 0):
		Global.pj_jugador = regiones.size()-1
	actualizar_pj(0)


func actualizar_pj(estado_boton):
	sprite_pj.region_enabled = true
	sprite_pj.region_rect = regiones[estado_boton][Global.pj_jugador]
	nombre_pj.text = Global.nombre_jugador


func _on_button_pj_seleccion_mouse_entered():
	actualizar_pj(1)


func _on_button_pj_seleccion_mouse_exited():
	actualizar_pj(0)


func _on_button_pj_seleccion_button_down():
	actualizar_pj(2)


func _on_button_pj_seleccion_pressed():
	Global.pj_jugador = Global.pj_jugador
	print("PJ seleccionado: ", Global.pj_jugador)
	get_tree().change_scene_to_file("res://scenes/pj_dialogue.tscn")


func _on_boton_volver_pressed() -> void:
	print("DEBUG: pressed EXIT menu button")
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
