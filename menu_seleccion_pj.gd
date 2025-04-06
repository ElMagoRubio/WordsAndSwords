extends Node2D

@onready var btn_ant = $TablaLarga/Control/ButtonPjAnterior
@onready var btn_sig = $TablaLarga/Control/ButtonPjSiguiente
@onready var sprite_pj = $TablaLarga/Control/PJSeleccionado
@onready var indice_pj = 0
@onready var regiones_normal = [
	Rect2(103, 1, 19, 46),  # Amolenth
	Rect2(32, 1, 20, 46),   # Baspiek
	Rect2(55, 1, 21, 46),   # Easttain
	Rect2(79, 1, 22, 46),   # Galeth
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


func _on_button_pj_anterior_pressed():
	indice_pj -= 1
	if (indice_pj < 0):
		indice_pj = regiones[1].size()-1
	actualizar_region(0)


func _on_button_pj_siguiente_pressed():
	indice_pj = (indice_pj + 1) % regiones.size()
	if (indice_pj < 0):
		indice_pj = regiones.size()-1
	actualizar_region(0)


func actualizar_region(estado_boton):
	sprite_pj.region_enabled = true
	sprite_pj.region_rect = regiones[estado_boton][indice_pj]


func _on_button_pj_seleccion_pressed():
	
