import hashlib
from collections import deque
from tetris_game.tetromino import Tetromino
from tetris_game.tetris import Tetris

MAX_MOVE_SEARCH_DEPTH = 30

def hash_grid(grid):
    """Generate a unique hash for the current grid configuration."""
    return hashlib.md5(str(grid).encode()).hexdigest()

def hash_piece_position(piece):
    """Generate a unique hash based on the piece's x, y, and rotation."""
    return f"{piece.x},{piece.y},{piece.rotation}"

def get_possible_moves_simulate(current_piece, grid):
    """
    Simulate all possible moves for the current Tetromino in the given grid.
    Returns x, y, and rotation for each possible final position.
    """
    explored_piece_positions = set()  # Deduplicate piece positions
    arrived_at_boards = set()  # Deduplicate hard-dropped boards
    bfs_queue = deque([(current_piece.clone(), [], grid)])  # Each item is (piece, commands, grid)
    possible_moves = []

    # Create a Tetris game instance to simulate moves
    tetris_game = Tetris(rows=len(grid), cols=len(grid[0]), block_size=30, window_width=600, window_height=800)
    tetris_game.grid = grid  # Set the initial grid

    while bfs_queue:
        piece, commands, current_grid = bfs_queue.popleft()

        # Skip already explored piece positions
        pos_hash = hash_piece_position(piece)
        if pos_hash in explored_piece_positions:
            continue
        explored_piece_positions.add(pos_hash)

        # Execute all commands (left, right, rotate, soft drop), but reserve hard drop as the final move
        if len(commands) < MAX_MOVE_SEARCH_DEPTH:
            for command in ['MOVE_LEFT', 'MOVE_RIGHT', 'ROTATE_CW', 'ROTATE_CCW', 'MOVE_DOWN']:
                # Simulate the Tetris game for this move
                new_tetris_game = Tetris(rows=len(current_grid), cols=len(current_grid[0]), block_size=30, window_width=600, window_height=800)
                new_tetris_game.grid = [row[:] for row in current_grid]  # Deep copy of the grid
                new_piece = piece.clone()  # Clone the current piece
                new_tetris_game.current_piece = new_piece  # Assign the cloned piece

                # Execute the command using Tetris methods
                if command == 'MOVE_LEFT':
                    new_tetris_game.move_left()
                elif command == 'MOVE_RIGHT':
                    new_tetris_game.move_right()
                elif command == 'MOVE_DOWN':
                    new_tetris_game.move_down()  # Soft drop
                elif command == 'ROTATE_CW':
                    new_tetris_game.rotate_cw()
                elif command == 'ROTATE_CCW':
                    new_tetris_game.rotate_ccw()

                # Append the result to the queue for further exploration
                bfs_queue.append((new_tetris_game.current_piece, commands + [command], new_tetris_game.grid))

        # Simulate hard drop as the last move
        if len(commands) < MAX_MOVE_SEARCH_DEPTH:
            new_tetris_game = Tetris(rows=len(current_grid), cols=len(current_grid[0]), block_size=30, window_width=600, window_height=800)
            new_tetris_game.grid = [row[:] for row in current_grid]  # Deep copy of the grid
            new_piece = piece.clone()  # Clone the current piece
            new_tetris_game.current_piece = new_piece  # Assign the cloned piece
            
            # Perform hard drop using the Tetris method
            new_tetris_game.hard_drop()  # This will move the piece down and lock it in place

            # Check if the board after the hard drop is unique
            board_hash = hash_grid(new_tetris_game.grid)
            if board_hash not in arrived_at_boards:
                arrived_at_boards.add(board_hash)
                # Print the commands leading to this move and the final position
                print(f"Commands: {commands + ['HARD_DROP']}")
                print(f"Final position: x={new_piece.x}, y={new_piece.y}, rotation={new_piece.rotation}")
                possible_moves.append((new_piece.x, new_piece.y, new_piece.rotation))

    return possible_moves
