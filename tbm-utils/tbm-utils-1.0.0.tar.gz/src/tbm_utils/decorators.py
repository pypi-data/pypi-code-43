__all__ = [
	'cast_to_list'
]

import wrapt


def cast_to_list(position):
	"""Cast the positional argument at given position into a list if not already a list."""

	@wrapt.decorator
	def wrapper(wrapped, instance, args, kwargs):
		if not isinstance(args[position], list):
			args = list(args)
			args[position] = [args[position]]
			args = tuple(args)

		return wrapped(*args, **kwargs)

	return wrapper
