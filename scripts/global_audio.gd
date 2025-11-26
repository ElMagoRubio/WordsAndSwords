extends Node

var audios: Dictionary = {}

func _ready() -> void:
	#Canciones
	_add_audio("audio_menu", "res://assets/Musica/main_menu.ogg")


func _add_audio(name: String, path: String) -> void:
	var player := AudioStreamPlayer.new()
	player.stream = load(path)
	add_child(player)
	audios[name] = player


func play_segment(name: String) -> void:
	if not audios.has(name):
		push_warning("Audio '%s' no encontrado." % name)
		return
	
	var player: AudioStreamPlayer = audios[name]
	if player.playing:
		player.stop()
	
	player.play()


func stop_play(name: String) -> void:
	if not audios.has(name):
		push_warning("Audio '%s' no encontrado." % name)
		return
		
	var player: AudioStreamPlayer = audios[name]
	if player.playing:
		player.stop()
