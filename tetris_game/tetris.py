import pygame
import random
import time
from tetris_game.controls import handle_input
from tetris_game.tetromino import Tetromino
from tetris_game.tetromino_data import COLORS
from tetris_game.score import calculate_score  # Import score calculation logic

class Tetris:
    def __init__(self, rows=21, cols=10, block_size=30, window_width=600, window_height=800):
        self.rows = rows
        self.cols = cols
        self.block_size = block_size
        self.window_width = window_width
        self.window_height = window_height

        # Calculate horizontal offset to center the board
        self.board_width = cols * block_size
        self.board_height = rows * block_size
        self.board_x_offset = (window_width - self.board_width) // 2

        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.current_piece = None
        self.hold_piece = None
        self.hold_used = False
        self.next_queue = self.generate_7_bag()
        self.next_piece()
        self.lines_cleared = 0
        self.start_time = time.time()
        self.score = 0
        self.game_over = False
        self.combo = -1  # Initialize combo to -1 (no combo yet)
        self.last_was_b2b = False  # Track if the last clear was eligible for B2B
        self.last_move_was_rotation = False  # Track if the last move was a rotation

    def generate_7_bag(self):
        """Generate the 7-bag of pieces."""
        bag = list(COLORS.keys())
        random.shuffle(bag)
        return bag

    def next_piece(self):
        """Move to the next piece."""
        if len(self.next_queue) < 6:
            self.next_queue.extend(self.generate_7_bag())
        piece_type = self.next_queue.pop(0)
        self.current_piece = Tetromino(piece_type)
        self.current_piece.x = 3  # Reset position
        self.hold_used = False  # Allow hold usage again

    def hold(self):
        """Hold the current piece, swap with the held piece if necessary."""
        if self.hold_used:
            return  # You can only hold once per piece drop

        if self.hold_piece:
            # Swap the current piece with the held piece
            self.current_piece, self.hold_piece = self.hold_piece, self.current_piece
            # Reset the current piece's position and rotation
            self.current_piece.x = 3
            self.current_piece.y = 0
            self.current_piece.rotation = 0
            self.current_piece.shape = self.current_piece.shape_data[0]  # Reset shape to initial orientation
        else:
            # Hold the current piece and fetch a new one
            self.hold_piece = self.current_piece
            self.next_piece()

        self.hold_piece.rotation = 0
        self.hold_piece.shape = self.hold_piece.shape_data[0]  # Reset the held piece's shape
        self.hold_used = True  # Mark that hold was used

    def update(self, key_input, event_list):
        if not self.game_over:
            handle_input(key_input, event_list, self)

        if key_input[pygame.K_LSHIFT] or key_input[pygame.K_RSHIFT]:
            self.reset_board_and_bag()

    def reset_board_and_bag(self):
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.next_queue = self.generate_7_bag()
        self.next_piece()
        self.hold_piece = None
        self.hold_used = False
        self.lines_cleared = 0
        self.score = 0
        self.combo = -1  # Reset combo
        self.start_time = time.time()

    def update_last_move(self, original_x, original_y, original_rotation, was_rotation):
        """Update the last move state to indicate if it actually moved or rotated the piece."""
        moved = (self.current_piece.x != original_x or 
                 self.current_piece.y != original_y or 
                 self.current_piece.rotation != original_rotation)
        self.last_move_was_rotation = was_rotation and moved
        return moved

    def move_left(self):
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        original_rotation = self.current_piece.rotation
        if self.current_piece.move(-1, 0, self.grid):
            self.update_last_move(original_x, original_y, original_rotation, was_rotation=False)

    def move_right(self):
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        original_rotation = self.current_piece.rotation
        if self.current_piece.move(1, 0, self.grid):
            self.update_last_move(original_x, original_y, original_rotation, was_rotation=False)

    def move_down(self):
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        original_rotation = self.current_piece.rotation
        if self.current_piece.move(0, 1, self.grid):
            self.update_last_move(original_x, original_y, original_rotation, was_rotation=False)

    def rotate_cw(self):
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate(self.grid, counterclockwise=False)
        self.update_last_move(original_x, original_y, original_rotation, was_rotation=True)

    def rotate_ccw(self):
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        original_rotation = self.current_piece.rotation
        self.current_piece.rotate(self.grid, counterclockwise=True)
        self.update_last_move(original_x, original_y, original_rotation, was_rotation=True)

    def hard_drop(self):
        """Immediately drop the piece to the lowest valid position."""
        original_x = self.current_piece.x
        original_y = self.current_piece.y
        original_rotation = self.current_piece.rotation

        while not self.current_piece.check_collision(self.grid, 0, 1):
            self.current_piece.move(0, 1, self.grid)
        
        # Only update last move if the drop changed x or y position
        if original_x != self.current_piece.x or original_y != self.current_piece.y:
            self.update_last_move(original_x, original_y, original_rotation, was_rotation=False)
        
        # Lock the piece and move to the next one
        self.lock_piece()
        self.next_piece()

    def is_immobile_spin(self):
        """Check if the current piece is in a true immobile spin position."""
        if not self.last_move_was_rotation:
            return False

        cannot_move_left = self.current_piece.check_collision(self.grid, -1, 0)
        cannot_move_right = self.current_piece.check_collision(self.grid, 1, 0)
        cannot_move_down = self.current_piece.check_collision(self.grid, 0, 1)
        
        if self.current_piece.type == 'T':
            corners_blocked = self.count_t_spin_corners()
            return (cannot_move_left and cannot_move_right and cannot_move_down) or (corners_blocked >= 3)

        return cannot_move_left and cannot_move_right and cannot_move_down

    def count_t_spin_corners(self):
        """Count the number of corners blocked around the T-piece."""
        corner_offsets = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        corner_count = 0
        for dx, dy in corner_offsets:
            corner_x = self.current_piece.x + dx
            corner_y = self.current_piece.y + dy
            if 0 <= corner_x < self.cols and 0 <= corner_y < self.rows:
                if self.grid[corner_y][corner_x] != 0:
                    corner_count += 1
        return corner_count

    def lock_piece(self):
        """Lock the current piece in place and check for line clears."""
        is_spin = self.is_immobile_spin()  # Detect spin status
        for i, row in enumerate(self.current_piece.shape):
            for j, value in enumerate(row):
                if value != 0:  # Only lock positions where there's a block
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = self.current_piece.type
        self.clear_lines(is_spin)

    def detect_clear_type(self, cleared_lines):
        """Determine the type of line clear (single, double, triple, or quad)."""
        if cleared_lines == 1:
            return "single"
        elif cleared_lines == 2:
            return "double"
        elif cleared_lines == 3:
            return "triple"
        elif cleared_lines == 4:
            return "quad"
        else:
            return None

    def detect_perfect_clear(self):
        """Check if the grid is completely empty (Perfect Clear detection)."""
        return all(all(cell == 0 for cell in row) for row in self.grid)

    def check_b2b(self, clear_type, is_spin):
        """Helper function to check if the current clear is a B2B."""
        return self.last_was_b2b and (clear_type == "quad" or is_spin)

    def clear_lines(self, is_spin):
        """Clear filled lines and shift the grid down."""
        new_grid = [row for row in self.grid if any(v == 0 for v in row)]
        cleared_lines = self.rows - len(new_grid)
        self.lines_cleared += cleared_lines
        new_grid = [[0 for _ in range(self.cols)] for _ in range(cleared_lines)] + new_grid
        self.grid = new_grid

        clear_type = self.detect_clear_type(cleared_lines)

        if cleared_lines > 0:
            is_b2b = self.check_b2b(clear_type, is_spin)
            if clear_type == "quad" or is_spin:
                self.last_was_b2b = True
            else:
                self.last_was_b2b = False
            self.combo += 1
            is_perfect_clear = self.detect_perfect_clear()
            self.score += calculate_score(
                cleared_lines, 
                is_spin=is_spin, 
                is_b2b=is_b2b, 
                combo=self.combo, 
                is_perfect_clear=is_perfect_clear
            )

            # Debug output including x, y, rotation state, piece type, and last move info
            print(
                f"Clear: {clear_type}, Spin: {is_spin}, B2B: {is_b2b}, Combo: {self.combo}, "
                f"PC: {is_perfect_clear}, Score: {self.score}, "
                f"Piece: {self.current_piece.type}, X: {self.current_piece.x}, "
                f"Y: {self.current_piece.y}, Rotation: {self.current_piece.rotation}, "
                f"Last Move Was Rotation: {self.last_move_was_rotation}"
            )
        else:
            self.combo = -1
            # print("Combo reset; no line clear.")

    def draw(self, screen):
        """Draw the current game state on the screen."""
        for x in range(self.cols):
            for y in range(self.rows):
                pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(
                    self.board_x_offset + x * self.block_size, y * self.block_size, self.block_size, self.block_size), 1)

        for y, row in enumerate(self.grid):
            for x, value in enumerate(row):
                if value != 0:
                    pygame.draw.rect(screen, COLORS[value], pygame.Rect(
                        self.board_x_offset + x * self.block_size, y * self.block_size, self.block_size, self.block_size))

        self.current_piece.draw(screen, self.block_size, self.board_x_offset)
        self.draw_hold(screen)
        self.draw_preview(screen)

        font = pygame.font.Font(None, 30)
        elapsed_time = time.time() - self.start_time
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, (255, 255, 255))
        time_text = font.render(f"Time: {int(elapsed_time)}s", True, (255, 255, 255))
        screen.blit(score_text, (self.board_x_offset + self.board_width + 20, 100))
        screen.blit(lines_text, (self.board_x_offset + self.board_width + 20, 140))
        screen.blit(time_text, (self.board_x_offset + self.board_width + 20, 180))

    def draw_hold(self, screen):
        """Draw the hold piece inside a smaller white box."""
        box_x = self.board_x_offset - 80  # Move left of the board
        box_y = 50
        box_size = self.block_size * 2  # Smaller box size

        pygame.draw.rect(screen, (255, 255, 255), (box_x, box_y, box_size, box_size), 2)

        if self.hold_piece:
            self.hold_piece.draw_hold(screen, self.block_size, box_x + self.block_size // 2, box_y + self.block_size // 2)

    def draw_preview(self, screen):
        """Draw the preview pieces inside smaller white boxes."""
        box_x = self.board_x_offset + self.board_width + 20
        box_size = self.block_size * 2

        for i in range(5):
            pygame.draw.rect(screen, (255, 255, 255), (box_x, 200 + i * (box_size + 10), box_size, box_size), 2)
            piece_type = self.next_queue[i]
            Tetromino(piece_type).draw_preview(screen, self.block_size, box_x + self.block_size // 2, 200 + i * (box_size + 10) + self.block_size // 2)
