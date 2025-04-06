extends Node2D

@onready var btn_ant = $TablaLarga/Control/ButtonPjAnterior
@onready var btn_sig = $TablaLarga/Control/ButtonPjSiguiente
@onready var sprite_pj = $TablaLarga/Control/PJSeleccionado
@onready var indice_pj = 0
@onready var regiones = [
	Rect2(100, 9, 19, 37),  # Amolenth
	Rect2(32, 7, 20, 39),   # Baspiek
	Rect2(54, 8, 21, 38),   # Easttain
	Rect2(77, 3, 22, 43),   # Galeth
	Rect2(1, 3, 29, 43)     # Vilgard
]


func _on_button_pj_anterior_pressed():
	indice_pj -= 1
	if (indice_pj < 0):
		indice_pj = regiones.size()-1
	actualizar_region()


func _on_button_pj_siguiente_pressed():
	indice_pj = (indice_pj + 1) % regiones.size()
	if (indice_pj < 0):
		indice_pj = regiones.size()-1
	actualizar_region()


func actualizar_region():
	sprite_pj.region_enabled = true
	sprite_pj.region_rect = regiones[indice_pj]
