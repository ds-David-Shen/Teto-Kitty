import pygame
from tetris_game.tetromino_data import COLORS, SHAPES, WALLKICKS, I_WALLKICKS, O_WALLKICKS

class Tetromino:
    def __init__(self, shape_key):
        self.shape_data = SHAPES[shape_key]  # Get all rotation states
        self.shape = self.shape_data[0]      # Start in the 0 rotation state
        self.x = 3                           # Initial x position
        self.y = 0                           # Initial y position
        self.rotation = 0                    # Start with rotation state 0
        self.type = shape_key
        self.was_rotated = False             # Track if the piece was rotated

    def clone(self):
        """
        Create a deep copy of the Tetromino instance.
        """
        # Initialize a new Tetromino of the same type
        cloned_tetromino = Tetromino(self.type)
        
        # Copy the position and rotation state
        cloned_tetromino.x = self.x
        cloned_tetromino.y = self.y
        cloned_tetromino.rotation = self.rotation
        cloned_tetromino.was_rotated = self.was_rotated
        
        # Set the shape to match the current rotation state
        cloned_tetromino.shape = self.shape_data[self.rotation]
        
        return cloned_tetromino
    
    def move(self, dx, dy, grid):
        """Move the piece by dx, dy if no collision and within grid bounds."""
        if not self.check_collision(grid, dx, dy):
            self.x += dx
            self.y += dy

    def rotate(self, grid, counterclockwise=False):
        """Rotate the tetromino using predefined states and check collision."""
        original_rotation = self.rotation

        # Update rotation index based on direction
        if counterclockwise:
            self.rotation = (self.rotation - 1) % len(self.shape_data)
        else:
            self.rotation = (self.rotation + 1) % len(self.shape_data)

        # Set shape to the new rotation state
        self.shape = self.shape_data[self.rotation]

        # Check if the new rotation causes a collision
        if not self.check_collision(grid):
            self.was_rotated = True  # Rotation occurred successfully
            return True
        else:
            # Apply wall kick or revert if unsuccessful
            if self.apply_wall_kick(grid, original_rotation, self.rotation):
                self.was_rotated = True
                return True
            else:
                # Revert rotation if wall kick fails
                self.shape = self.shape_data[original_rotation]
                self.rotation = original_rotation
                self.was_rotated = False
                return False

    def apply_wall_kick(self, grid, original_rotation, new_rotation):
        """Attempt to apply a wall kick based on the tetromino's rotation state."""
        key = f"{original_rotation}-{new_rotation}"  # Define rotation transition key

        # Select the appropriate wall kick table based on the tetromino type
        if self.type == 'I':
            kicks = I_WALLKICKS
        elif self.type == 'O':
            kicks = O_WALLKICKS
        else:
            kicks = WALLKICKS

        # Attempt each offset in the wall kick data
        for offset_x, offset_y in kicks.get(key, []):
            if not self.check_collision(grid, offset_x, -offset_y):  # Invert y offset because positive y is up
                self.x += offset_x
                self.y -= offset_y
                return True  # Wall kick successful

        return False  # No valid wall kick found

    def check_collision(self, grid, offset_x=0, offset_y=0):
        """Check if the current position of the tetromino collides with the grid or is out of bounds."""
        for i, row in enumerate(self.shape):
            for j, value in enumerate(row):
                if value != 0:  # Only check solid blocks
                    x = self.x + j + offset_x
                    y = self.y + i + offset_y

                    # Check if the piece is out of bounds
                    if x < 0 or x >= len(grid[0]) or y >= len(grid):
                        return True  # Collision detected (out of bounds)

                    # Check if the piece collides with another block in the grid
                    if y >= 0 and grid[y][x] != 0:
                        return True  # Collision detected (with a locked piece)
        return False  # No collision

    def draw(self, screen, block_size, x_offset):
        """Draw the piece on the screen."""
        for i, row in enumerate(self.shape):
            for j, value in enumerate(row):
                if value != 0:
                    pygame.draw.rect(screen, COLORS[self.type], pygame.Rect(
                        x_offset + (self.x + j) * block_size, (self.y + i) * block_size, block_size, block_size))

    def draw_preview(self, screen, block_size, offset_x, offset_y):
        """Draw the preview piece at a smaller size."""
        for i, row in enumerate(self.shape):
            for j, value in enumerate(row):
                if value != 0:
                    pygame.draw.rect(screen, COLORS[self.type], pygame.Rect(
                        offset_x + j * block_size // 2, offset_y + i * block_size // 2, block_size // 2, block_size // 2))

    def draw_hold(self, screen, block_size, offset_x, offset_y):
        """Draw the held piece."""
        for i, row in enumerate(self.shape):
            for j, value in enumerate(row):
                if value != 0:
                    pygame.draw.rect(screen, COLORS[self.type], pygame.Rect(
                        offset_x + j * block_size // 2, offset_y + i * block_size // 2, block_size // 2, block_size // 2))

def lock_piece_in_grid(piece, grid):
    """
    Lock the current piece in the grid after performing a hard drop.
    """
    for i, row in enumerate(piece.shape):
        for j, value in enumerate(row):
            if value != 0:  # Only lock solid blocks
                grid[piece.y + i][piece.x + j] = piece.type
