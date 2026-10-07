from rps import is_move_good
from rps import is_round_winner
from rps import get_name

# Test case 1: Invalid move (int)
# Expected output: False
# Actual output: False
print(is_move_good(19))

# Test case 2: No move
# Expected output: False
# Actual output: False
print(is_move_good(""))

# Test case 3: Invalid opponent move
# Expected output: True
# Actual output: True
print(is_round_winner("p", "argmagagdvbd"))

# Test case 4: Both invalid moves
# Expected output: False
# Actual output: False
print(is_round_winner("fsdffg", "123424"))

# Test case 5: bad player number
# Expected output: Error
# Actual output: Error (returning a value that was never set)
print(get_name("steve"))

# Test case 5: input invalid name
# Expected output: prints error, then corrects name
# Actual output: correct, entering invalid name sets the name to the default
print(get_name(1))