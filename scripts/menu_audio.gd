extends HSlider

@export
var bus_nombre: String
var bus_id: int

func _ready() -> void:
	bus_id = AudioServer.get_bus_index(bus_nombre)
	value_changed.connect(_on_value_changed)

func _on_value_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(
		bus_id, 
		linear_to_db(value))
