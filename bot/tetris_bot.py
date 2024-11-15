import sys
import os
import time
import pygame
import random  # Import random for selecting a random valid move
from bot.get_valid_moves import get_possible_moves_simulate  # Import the valid moves function

# Add the path to the tetris_game directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../tetris_game')))

from tetris import Tetris  # Import the Tetris game class

class TetrisBot:
    def __init__(self, max_moves=10):
        self.game_state = Tetris()  # Initialize a new Tetris game state
        self.move_count = 0  # Counter for the number of moves made
        self.active = True  # Flag to control whether the bot is active
        self.max_moves = max_moves  # Set maximum moves allowed
        self.max_moves_reached_printed = False  # Flag to print maximum moves message only once
        self.valid_moves = []  # Store valid moves for random selection

    def print_board(self, grid):
        """Print the last four rows of a given grid to the console."""
        print("Current Board (last four rows):")
        for row in grid[-4:]:  # Only print the last four rows
            print(' '.join(str(cell) if cell != 0 else '.' for cell in row))
        print("\n")

    def print_all_moves(self):
        """Print all valid moves found for the current Tetromino."""
        if not self.valid_moves:
            print("No valid moves to display.")
            return

        print(f"Number of valid moves found: {len(self.valid_moves)}")
        for i, (x, y, rotation) in enumerate(self.valid_moves):
            print(f"Move {i + 1}/{len(self.valid_moves)}: Place piece at ({x}, {y}) with rotation {rotation}")
        print()  # Blank line for separation

    def random_move(self):
        """Select a random move from valid moves and print the move number."""
        self.valid_moves = get_possible_moves_simulate(self.game_state.current_piece, self.game_state.grid)  # Get valid moves using simulation
        if self.valid_moves:  # Ensure there are valid moves
            move_index = random.randint(0, len(self.valid_moves) - 1)  # Select a random index
            x, y, rotation = self.valid_moves[move_index]
            
            # Print the selected move with its number out of total valid moves
            print(f"Random move selected: Place piece at ({x}, {y}) with rotation {rotation} ({move_index + 1}/{len(self.valid_moves)})")
            return x, y, rotation
        else:
            print("No valid moves available.")
            return None, None, None

    def make_move(self):
        if self.move_count < self.max_moves:  # Use the max_moves variable
            # Print the current board state first
            self.print_board(self.game_state.grid)

            x, y, rotation = self.random_move()  # Get a random move
            if x is not None and y is not None:  # Ensure the move is valid
                # Set the current piece's position and rotation
                current_piece = self.game_state.current_piece
                current_piece.rotation = rotation
                current_piece.x = x
                current_piece.y = y  # Move to the calculated position

                # Check for collision at the final position before locking the piece
                if y >= 0 and not current_piece.check_collision(self.game_state.grid):
                    # Lock the piece after moving
                    self.game_state.lock_piece()
                    self.game_state.next_piece()   # Get the next piece after locking
                    
                    self.move_count += 1  # Increment move counter

                    # Print all valid configurations after the move
                    self.print_all_moves()
                    
                    # Print the current board state after the move
                    self.print_board(self.game_state.grid)
                    
                    time.sleep(1)  # Delay to visualize the move
                    self.draw()  # Draw the current game state
                else:
                    print(f"Collision detected, cannot place piece at ({x}, {y}).")
            else:
                print("No valid moves available.")
        else:
            if not self.max_moves_reached_printed:
                print("Maximum moves reached. Bot will stop placing pieces.")
                self.max_moves_reached_printed = True  # Set the flag to prevent multiple prints
            self.active = False  # Stop the bot's activity

    def draw(self):
        """Draw the current game state on the screen."""
        screen.fill((0, 0, 0))  # Clear the screen
        self.game_state.draw(screen)  # Call the draw method of Tetris to render the game state
        pygame.display.flip()  # Update the display

# Example usage
if __name__ == "__main__":
    pygame.init()
    window_width, window_height = 600, 21 * 30  # Same size as your main game window
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Tetris Bot Visualization")

    bot = TetrisBot(max_moves=10)  # Set the maximum moves allowed

    running = True
    while running and not bot.game_state.game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        bot.make_move()  # The bot attempts to make a move

    # Keep the window open after the bot stops placing pieces
    while bot.active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bot.active = False

    pygame.quit()
