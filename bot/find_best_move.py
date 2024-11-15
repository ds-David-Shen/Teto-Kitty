import math
from bot.get_possible_moves import get_possible_moves_simulate  # Import the valid moves function

def evaluate_board(grid):
    """Evaluate the board state and return a score."""
    score = 0
    filled_lines = sum(1 for row in grid if all(cell != 0 for cell in row))
    score += filled_lines * 100  # Score for lines cleared

    # Penalize based on the maximum height of the columns
    column_heights = [0] * len(grid[0])
    for x in range(len(grid[0])):
        for y in range(len(grid)):
            if grid[y][x] != 0:
                column_heights[x] = len(grid) - y
                break
    max_height = max(column_heights)
    score -= max_height * 2  # Penalize tall stacks

    return score

def alpha_beta_pruning(grid, depth, alpha, beta, maximizing_player, valid_moves):
    """Perform alpha-beta pruning to find the best move."""
    if depth == 0:
        return evaluate_board(grid), None  # Return the score and no move

    best_move = None

    if maximizing_player:
        max_eval = -math.inf
        for x, y, rotation in valid_moves:
            # Generate a new grid based on the move
            new_grid = [row[:] for row in grid]
            # Apply the move by placing the piece in `new_grid`
            # Placeholder: replace with actual piece placement logic
            evaluation = alpha_beta_pruning(new_grid, depth - 1, alpha, beta, False, valid_moves)[0]
            if evaluation > max_eval:
                max_eval = evaluation
                best_move = (x, y, rotation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval, best_move

    else:
        min_eval = math.inf
        for x, y, rotation in valid_moves:
            # Generate a new grid based on the move
            new_grid = [row[:] for row in grid]
            # Apply the move by placing the piece in `new_grid`
            # Placeholder: replace with actual piece placement logic
            evaluation = alpha_beta_pruning(new_grid, depth - 1, alpha, beta, True, valid_moves)[0]
            if evaluation < min_eval:
                min_eval = evaluation
                best_move = (x, y, rotation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval, best_move

def find_best_move(current_piece, grid, depth=3):
    """Find the best move using alpha-beta pruning."""
    # Precompute all valid moves for the current piece and grid
    valid_moves = get_possible_moves_simulate(current_piece, grid)
    best_score, best_move = alpha_beta_pruning(grid, depth, -math.inf, math.inf, True, valid_moves)
    return best_move  # Return the best move found
