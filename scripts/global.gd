extends Node

var _lista_nombres = [
	"Amolenth",
	"Baspiek",
	"Easttain",
	"Galeth",
	"Vilgard"
]

var _nombre_jugador = "Amolenth"
var nombre_jugador:
	get:
		return _nombre_jugador

var _pj_jugador = 0
var pj_jugador:
	get:
		return _pj_jugador
	
	set(value):
		_pj_jugador = value
		_nombre_jugador = _lista_nombres[_pj_jugador]

var _rutas_imagenes = [
	"res://assets/PJS/Amolenth/Amolenth.png",
	"res://assets/PJS/Baspiek/Baspiek.png",
	"res://assets/PJS/Easttain/Easttain.png",
	"res://assets/PJS/Galeth/Galeth.png",
	"res://assets/PJS/Vilgard/Vilgard.png"
]
var rutas_imagenes:
	get:
		return _rutas_imagenes

var _rendicion_jugador = false
var rendicion_jugador:
	get:
		return _rendicion_jugador
	
	set(value):
		_rendicion_jugador = value
		_combate = !value

var _combate = false
var combate:
	get:
		return _combate
	
	set(value):
		_combate = value
		_rendicion_jugador = !value
