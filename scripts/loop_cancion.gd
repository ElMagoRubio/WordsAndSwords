extends AudioStreamPlayer

func _ready():
	if stream:
		stream.loop = true
	play()
