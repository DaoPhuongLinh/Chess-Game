# Combined Chess Game

import pygame
import sys
import random
import time
import math
import numpy as np
from copy import deepcopy

# Khởi tạo pygame
pygame.init()

# Các hằng số và màu sắc (prioritize game 2 for larger dimensions and colors)
WIDTH, HEIGHT = 650, 650
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19) # Used for menu background
CREAM = (240, 217, 181) # Used for light squares
DARK_BLUE = (0, 0, 139) # Used for background in game 2
HIGHLIGHT = (100, 255, 100) # From Chess (1).py
SELECT_COLOR = (255, 255, 0) # From Chess (1).py
HOVER_COLOR = (100, 100, 255) # From giaodien2 (2).py and Chess (1).py, use one

# Cài đặt cửa sổ
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Cờ Vua')

# Tạo font chữ (prioritize game 2's font handling)
try:
    # Cố gắng sử dụng font hỗ trợ ký tự đặc biệt và biểu tượng cờ vua
    font = pygame.font.SysFont('segoe ui symbol', SQUARE_SIZE // 2)
    # Nếu font trên không có hoặc không hiển thị đúng, thử font khác
    if font is None or not font.get_linesize(): # Check if font creation failed or size is zero
         font = pygame.font.SysFont('arial unicode ms', SQUARE_SIZE // 2)
    if font is None or not font.get_linesize():
         font = pygame.font.SysFont('DejaVu Sans', SQUARE_SIZE // 2) # Phổ biến trên Linux
    if font is None or not font.get_linesize():
         font = pygame.font.SysFont('Arial', SQUARE_SIZE // 2) # Fallback
except Exception as e:
    print(f"Lỗi khi tạo font: {e}")
    # Fallback to a basic font if font creation fails
    font = pygame.font.SysFont('arial', SQUARE_SIZE // 2)

small_font = pygame.font.SysFont('arial', 20)
large_font = pygame.font.SysFont('arial', 50)


# Bảng điểm vị trí cho từng quân cờ (from game 2)
POSITION_WEIGHTS = {
    'p': np.array([
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
        [0.5, 1, 1, -2, -2, 1, 1, 0.5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]),
    'N': np.array([
        [-5, -4, -3, -3, -3, -3, -4, -5],
        [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
        [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
        [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
        [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
        [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
        [-4, -2, 0, 0, 0, 0, -2, -4],
        [-5, -4, -3, -3, -3, -3, -4, -5]
    ]),
    'B': np.array([
        [-2, -1, -1, -1, -1, -1, -1, -2],
        [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
        [-1, 1, 1, 1, 1, 1, 1, -1],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
        [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-2, -1, -1, -1, -1, -1, -1, -2]
    ]),
    'R': np.array([
        [0, 0, 0, 0.5, 0.5, 0, 0, 0],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [0.5, 1, 1, 1, 1, 1, 1, 0.5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]),
    'Q': np.array([
        [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
        [-1, 0.5, 0.5, 0, 0, 0, 0, -1],
        [-1, 0.5, 1, 1, 1, 1, 0.5, -1],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [-0.5, 0, 1, 1, 1, 1, 0, -0.5],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-2, -1, -1, -0.5, -0.5, -1, -1, -2]
    ]),
    'K': np.array([
        [2, 3, 1, 0, 0, 1, 3, 2],
        [2, 2, 0, 0, 0, 0, 2, 2],
        [-1, -2, -2, -2, -2, -2, -2, -1],
        [-2, -3, -3, -4, -4, -3, -3, -2],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3]
    ])
}

# Giá trị các quân cờ (from game 2) - ĐÃ TĂNG GIÁ TRỊ CỦA TỐT CHO AI ƯU TIÊN ĂN HƠN
PIECE_VALUES = {
    'p': 150,  # Tăng giá trị của tốt
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 20000
}

# Tạo các quân cờ bằng text (from game 2)
def create_pieces():
    pieces = {}
    # Quân trắng
    pieces['wp'] = font.render('♙', True, WHITE)
    pieces['wN'] = font.render('♘', True, WHITE)
    pieces['wB'] = font.render('♗', True, WHITE)
    pieces['wR'] = font.render('♖', True, WHITE)
    pieces['wQ'] = font.render('♕', True, WHITE)
    pieces['wK'] = font.render('♔', True, WHITE)
    # Quân đen
    pieces['bp'] = font.render('♟', True, BLACK)
    pieces['bN'] = font.render('♞', True, BLACK)
    pieces['bB'] = font.render('♝', True, BLACK)
    pieces['bR'] = font.render('♜', True, BLACK)
    pieces['bQ'] = font.render('♛', True, BLACK)
    pieces['bK'] = font.render('♚', True, BLACK)
    return pieces

# Class Move (from game 2)
class Move:
    def __init__(self, start, end, piece_moved, piece_captured=None, is_pawn_promotion=False):
        self.start = start
        self.end = end
        self.piece_moved = piece_moved
        self.piece_captured = piece_captured
        self.is_pawn_promotion = is_pawn_promotion

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.start == other.start and self.end == other.end

    def __str__(self):
        # This might be printed to console, ensure it handles potential characters
        # Use .encode('utf-8', 'replace').decode('utf-8') as a defensive measure if environment encoding is stubborn
        try:
            return f"{self.piece_moved} from {self.start} to {self.end}"
        except UnicodeEncodeError:
             return f"Move from {self.start} to {self.end}" # Fallback if encoding fails

# Base Piece class (from Chess (1).py, adapted to game 2's move structure)
class Piece:
    def __init__(self, color):
        self.color = color

    def get_moves(self, board, row, col):
        return []

# Piece classes (adapted from Chess (1).py to use game 2's get_moves structure and Move class)
class King(Piece):
    def __str__(self):
        return 'K' if self.color == 'w' else 'k'

    def get_moves(self, board, row, col):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                    target = board[new_row][new_col]
                    if target == '--' or target[0] != self.color:
                        moves.append(Move((row, col), (new_row, new_col), board[row][col], target))
        return moves

class Queen(Piece):
    def __str__(self):
        return 'Q' if self.color == 'w' else 'q'

    def get_moves(self, board, row, col):
        return Rook(self.color).get_moves(board, row, col) + Bishop(self.color).get_moves(board, row, col)

class Rook(Piece):
    def __str__(self):
        return 'R' if self.color == 'w' else 'r'

    def get_moves(self, board, row, col):
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = row + dr * i
                new_col = col + dc * i
                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                    target = board[new_row][new_col]
                    if target == '--':
                        moves.append(Move((row, col), (new_row, new_col), board[row][col], board[new_row][new_col]))
                    elif target[0] != self.color:
                        moves.append(Move((row, col), (new_row, new_col), board[row][col], board[new_row][new_col]))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Bishop(Piece):
    def __str__(self):
        return 'B' if self.color == 'w' else 'b'

    def get_moves(self, board, row, col):
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row = row + dr * i
                new_col = col + dc * i
                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                    target = board[new_row][new_col]
                    if target == '--':
                        moves.append(Move((row, col), (new_row, new_col), board[row][col], board[new_row][new_col]))
                    elif target[0] != self.color:
                        moves.append(Move((row, col), (new_row, new_col), board[row][col], board[new_row][new_col]))
                        break
                    else:
                        break
                else:
                    break
        return moves

class Knight(Piece):
    def __str__(self):
        return 'N' if self.color == 'w' else 'n'

    def get_moves(self, board, row, col):
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                target = board[new_row][new_col]
                if target == '--' or target[0] != self.color:
                    moves.append(Move((row, col), (new_row, new_col), board[row][col], target))
        return moves

class Pawn(Piece):
    def __str__(self):
        return 'P' if self.color == 'w' else 'p'

    def get_moves(self, board, row, col):
        moves = []
        direction = -1 if self.color == 'w' else 1
        start_row = 6 if self.color == 'w' else 1

        # Di chuyển tiến 1 ô
        if 0 <= row + direction < ROWS and board[row + direction][col] == '--':
            is_promotion = (self.color == 'w' and row + direction == 0) or (self.color == 'b' and row + direction == 7)
            moves.append(Move((row, col), (row + direction, col), board[row][col], board[row + direction][col], is_promotion))
            # Di chuyển tiến 2 ô từ vị trí ban đầu
            if row == start_row and board[row + 2 * direction][col] == '--':
                moves.append(Move((row, col), (row + 2 * direction, col), board[row][col], board[row + 2 * direction][col]))

        # Ăn quân chéo
        for d_col in [-1, 1]:
            if 0 <= col + d_col < COLS and 0 <= row + direction < ROWS:
                target = board[row + direction][col + d_col]
                if target != '--' and target[0] != self.color:
                    is_promotion = (self.color == 'w' and row + direction == 0) or (self.color == 'b' and row + direction == 7)
                    moves.append(Move((row, col), (row + direction, col + d_col), board[row][col], target, is_promotion))
        return moves

# Lớp quản lý bàn cờ (from game 2, with adaptation for piece movement)
class Board:
    def __init__(self):
        self.board = []
        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.create_board()

    def draw_squares(self, screen):
        colors = [CREAM, BROWN]
        for row in range(ROWS):
            for col in range(COLS):
                color = colors[(row + col) % 2]
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        # Cập nhật vị trí vua khi khởi tạo
        self.white_king = (7, 4)
        self.black_king = (0, 4)

    def draw(self, screen, pieces, selected_square=None, valid_moves=[]):
        self.draw_squares(screen)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != '--':
                    piece_text = pieces[piece]
                    text_rect = piece_text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                    row * SQUARE_SIZE + SQUARE_SIZE // 2))
                    screen.blit(piece_text, text_rect)

                if selected_square == (row, col):
                    pygame.draw.rect(screen, SELECT_COLOR, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

        for move in valid_moves:
            row, col = move.end
            pygame.draw.circle(screen, BLUE,
                             (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                              row * SQUARE_SIZE + SQUARE_SIZE // 2),
                             10)


    def move(self, move):
        start_row, start_col = move.start
        end_row, end_col = move.end
        piece = self.board[start_row][start_col]

        # Cập nhật vị trí vua
        if piece == 'wK':
            self.white_king = (end_row, end_col)
        elif piece == 'bK':
            self.black_king = (end_row, end_col)

        # Thực hiện di chuyển
        self.board[start_row][start_col] = '--'
        self.board[end_row][end_col] = move.piece_moved

        # Phong cấp tốt
        if move.is_pawn_promotion:
            self.board[end_row][end_col] = move.piece_moved[0] + 'Q'

    def get_valid_moves(self, color):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != '--' and piece[0] == color:
                    self.get_piece_moves(row, col, moves)

        # Lọc các nước đi gây chiếu tướng
        valid_moves = []
        for move in moves:
            temp_board = deepcopy(self)
            temp_board.move(move)

            # Kiểm tra không bị chiếu sau khi di chuyển
            if not temp_board.is_in_check(color):
                valid_moves.append(move)

        return valid_moves

    def get_piece_moves(self, row, col, moves):
        piece_code = self.board[row][col]
        if piece_code == '--':
            return

        color = piece_code[0]
        kind = piece_code[1]

        piece_classes = {
            'p': Pawn,
            'N': Knight,
            'B': Bishop,
            'R': Rook,
            'Q': Queen,
            'K': King
        }

        if kind in piece_classes:
            piece_class = piece_classes[kind]
            piece = piece_class(color)

            piece_moves = piece.get_moves(self.board, row, col)
            moves.extend(piece_moves)


    def is_in_check(self, color):
        king_pos = self.white_king if color == 'w' else self.black_king
        opponent_color = 'b' if color == 'w' else 'w'
        
        # Kiểm tra tất cả quân đối phương
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != '--' and piece[0] == opponent_color:
                    # Lấy tất cả nước đi có thể của quân đối phương
                    temp_moves = []
                    self.get_piece_moves(row, col, temp_moves)
                    for move in temp_moves:
                        if move.end == king_pos:
                            return True
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
    # Kiểm tra xem có bất kỳ nước đi nào thoát khỏi chiếu không
        return len(self.get_valid_moves(color)) == 0

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        return len(self.get_valid_moves(color)) == 0

    def evaluate(self):
        score = 0

        # Đánh giá theo giá trị quân cờ
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != '--':
                    value = PIECE_VALUES.get(piece[1], 0)

                    # Thêm trọng số vị trí
                    if piece[0] == 'w':
                        score += value
                        if piece[1] in POSITION_WEIGHTS:
                            score += POSITION_WEIGHTS[piece[1]][row][col] * 10
                    else:
                        # ĐÃ TĂNG ĐIỂM KHI ĂN QUÂN TRẮNG
                        score -= value * 1.2 # Tăng điểm khi ăn quân trắng
                        if piece[1] in POSITION_WEIGHTS:
                            score -= POSITION_WEIGHTS[piece[1]][7 - row][col] * 10  # Đảo ngược cho quân đen

        # Thêm điểm cho kiểm soát trung tâm
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for r, c in center_squares:
            piece = self.board[r][c]
            if piece != '--':
                if piece[0] == 'w':
                    score += 5
                else:
                    score -= 5

        return score

# Lớp Game cho Human vs Human (adapted from Chess (1).py)
class HumanVsHumanGame:
    def __init__(self):
        self.board = Board()
        self.pieces = create_pieces()
        self.turn = "w"
        self.running = True
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.message = ""
        self.game_result_message = "" # Store the final game result message

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)

            if not self.game_over:
                screen.fill(WHITE)
                self.board.draw(screen, self.pieces, self.selected, self.valid_moves)
                self.draw_status()
            else:
                self.draw_game_over_screen()

            pygame.display.flip()
            self.handle_events()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_over:
                    self.handle_click(*pygame.mouse.get_pos())
                else:
                    # Handle click on game over screen (e.g., return to menu)
                    mouse_pos = pygame.mouse.get_pos()
                    if self.return_button_rect.collidepoint(mouse_pos):
                         self.running = False # Exit game loop to return to menu

    def handle_click(self, mx, my):
        x = mx // SQUARE_SIZE
        y = my // SQUARE_SIZE
        piece = self.board.board[y][x]

        if self.selected:
            move = self.get_move(self.selected, (y, x))
            if move is not None and move in self.valid_moves:
                self.board.move(move)
                self.turn = "b" if self.turn == "w" else "w"
                self.check_game_over()
            self.selected = None
            self.valid_moves = []
        elif piece != '--' and piece[0] == self.turn:
            self.selected = (y, x)
            self.valid_moves = [m for m in self.board.get_valid_moves(self.turn)
                               if m.start == (y, x)]

    def get_move(self, start, end):
        # Need to generate valid moves for the selected piece to find the move object
        row, col = start
        piece_code = self.board.board[row][col]
        color = piece_code[0]
        kind = piece_code[1]
        piece_classes = {
            'p': Pawn, 'N': Knight, 'B': Bishop, 'R': Rook, 'Q': Queen, 'K': King
        }
        if kind in piece_classes:
            piece_class = piece_classes[kind]
            piece = piece_class(color)
            all_possible_moves_for_piece = piece.get_moves(self.board.board, row, col)
            # Filter to get only valid moves (checking for check)
            valid_moves_for_piece = []
            for move in all_possible_moves_for_piece:
                temp_board = deepcopy(self.board)
                temp_board.move(move)
                if not temp_board.is_in_check(color):
                    valid_moves_for_piece.append(move)

            for move in valid_moves_for_piece:
                if move.end == end:
                    return move
        return None


    def draw_status(self):
        # This string contains Vietnamese characters
        turn_text = f"Lượt: {'Trắng' if self.turn == 'w' else 'Đen'}"
        text = small_font.render(turn_text, True, BLACK)
        screen.blit(text, (10, HEIGHT - 40))

        if self.message:
            # This string might contain Vietnamese characters from game over messages
            msg_text = small_font.render(self.message, True, RED)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT - 40))

    def check_game_over(self):
        if self.board.is_checkmate(self.turn):
            self.game_over = True
            winner_color = "Đen" if self.turn == "w" else "Trắng"
            # This message contains Vietnamese characters
            self.game_result_message = f"Chiếu bí! {winner_color} thắng!"
        elif self.board.is_stalemate(self.turn):
            self.game_over = True
            # This message contains Vietnamese characters
            self.game_result_message = "Hòa cờ!"

    def draw_game_over_screen(self):
        screen.fill(BLACK) # Black background for game over screen

        # Display the result message
        result_text = large_font.render(self.game_result_message, True, WHITE)
        result_rect = result_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(result_text, result_rect)

        # Draw a button to return to the menu
        mouse_pos = pygame.mouse.get_pos()
        self.return_button_rect = draw_button("Return to Menu", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, mouse_pos)

# Lớp Game cho Human vs AI (from game 2)
class HumanVsAIGame:
    def __init__(self):
        self.board = Board()
        self.pieces = create_pieces()
        self.human_color = 'w'
        self.ai_color = 'b'
        self.turn = self.human_color
        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.message = ""
        self.ai_thinking = False
        self.last_ai_move_time = 0
        self.running = True
        self.game_result_message = "" # Store the final game result message


    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.game_over:
                        pos = pygame.mouse.get_pos()
                        if pos[1] < HEIGHT - 50:  # Chỉ xử lý click trên bàn cờ
                            col = pos[0] // SQUARE_SIZE
                            row = pos[1] // SQUARE_SIZE

                            if 0 <= row < ROWS and 0 <= col < COLS:
                                self.select(row, col)
                    else:
                        # Handle click on game over screen (e.g., return to menu)
                        mouse_pos = pygame.mouse.get_pos()
                        if self.return_button_rect.collidepoint(mouse_pos):
                            self.running = False # Exit game loop to return to menu


            if not self.game_over:
                # Xử lý lượt đi của AI
                if not self.ai_thinking and self.turn == self.ai_color:
                     self.ai_thinking = True
                     self.last_ai_move_time = time.time()

                if self.ai_thinking and time.time() - self.last_ai_move_time > 0.5:  # Thêm độ trễ để người chơi thấy AI "suy nghĩ"
                     self.ai_move()

                self.update()
            else:
                self.draw_game_over_screen()


            clock.tick(60)


    def update(self):
        screen.fill(DARK_BLUE)
        self.board.draw(screen, self.pieces, self.selected, self.valid_moves)
        self.draw_status()
        pygame.display.update()

    def draw_valid_moves(self):
        if self.selected:
            for move in self.valid_moves:
                if move.start == self.selected:
                    row, col = move.end
                    pygame.draw.circle(screen, BLUE,
                                     (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                      row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                     10)

    def draw_status(self):
        # This string contains Vietnamese characters
        turn_text = f"Lượt: {'Người' if self.turn == self.human_color else 'Máy'}"
        text = small_font.render(turn_text, True, WHITE)
        screen.blit(text, (10, HEIGHT - 40))

        if self.message:
            # This string might contain Vietnamese characters from game over messages
            msg_text = small_font.render(self.message, True, RED)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT - 40))

        if self.ai_thinking:
            # This string contains Vietnamese characters
            think_text = small_font.render("AI đang suy nghĩ...", True, GREEN)
            screen.blit(think_text, (WIDTH - 150, HEIGHT - 40))


    def select(self, row, col):
        if self.game_over or self.ai_thinking or self.turn != self.human_color:
            return False

        piece = self.board.board[row][col]

        # Nếu đã chọn quân cờ và chọn ô khác để di chuyển
        if self.selected:
            move = self.get_move(self.selected, (row, col))
            if move is not None and move in self.valid_moves:
                self.make_move(move)
                self.selected = None
                self.valid_moves = []

                # Kiểm tra kết thúc trò chơi
                self.check_game_over()

                # Nếu game chưa kết thúc, đến lượt AI
                if not self.game_over:
                    self.turn = self.ai_color


                return True
            else:
                # Nếu chọn quân cờ khác cùng màu
                if piece != '--' and piece[0] == self.human_color:
                    self.selected = (row, col)
                    self.valid_moves = [m for m in self.board.get_valid_moves(self.human_color)
                                       if m.start == (row, col)]
                    return True
                else:
                    self.selected = None
                    self.valid_moves = []
                    return False

        # Chọn quân cờ
        if piece != '--' and piece[0] == self.human_color:
            self.selected = (row, col)
            self.valid_moves = [m for m in self.board.get_valid_moves(self.human_color)
                               if m.start == (row, col)]
            return True

        return False

    def get_move(self, start, end):
         # Need to generate valid moves for the selected piece to find the move object
        row, col = start
        piece_code = self.board.board[row][col]
        color = piece_code[0]
        kind = piece_code[1]
        piece_classes = {
            'p': Pawn, 'N': Knight, 'B': Bishop, 'R': Rook, 'Q': Queen, 'K': King
        }
        if kind in piece_classes:
            piece_class = piece_classes[kind]
            piece = piece_class(color)
            all_possible_moves_for_piece = piece.get_moves(self.board.board, row, col)
            # Filter to get only valid moves (checking for check)
            valid_moves_for_piece = []
            for move in all_possible_moves_for_piece:
                temp_board = deepcopy(self.board)
                temp_board.move(move)
                if not temp_board.is_in_check(color):
                    valid_moves_for_piece.append(move)

            for move in valid_moves_for_piece:
                if move.end == end:
                    return move
        return None


    def make_move(self, move):
        self.board.move(move)


    def ai_move(self):
        if self.game_over:
            return

        start_time = time.time()
        best_move = self.find_best_move()
        if best_move:
            self.make_move(best_move)
            # Removed the print statement causing UnicodeEncodeError

        # Kiểm tra kết thúc trò chơi sau khi AI đi
        self.check_game_over()

        end_time = time.time()
        # Removed the print statement causing UnicodeEncodeError
        self.ai_thinking = False
        # Nếu game chưa kết thúc, đến lượt người chơi
        if not self.game_over:
            self.turn = self.human_color


    def find_best_move(self):
        best_move = None
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf
        depth = 3  # Tăng độ sâu tìm kiếm

        valid_moves = self.board.get_valid_moves(self.ai_color)

        # Nếu không có nước đi hợp lệ, trả về None (trường hợp bế tắc/chiếu bí đã được xử lý ở cấp game)
        if not valid_moves:
             return None

        # Sắp xếp các nước đi theo heuristic để cắt tỉa hiệu quả hơn
        valid_moves.sort(key=lambda m: self.move_heuristic(m), reverse=True)


        for move in valid_moves:
            temp_board = deepcopy(self.board)
            temp_board.move(move)

            # Sử dụng Minimax với cắt tỉa Alpha-Beta
            board_value = self.minimax(temp_board, depth - 1, False, alpha, beta)

            if board_value > best_value:
                best_value = board_value
                best_move = move

            alpha = max(alpha, best_value)
            if beta <= alpha:
                break

        return best_move

    def move_heuristic(self, move):
        # Heuristic đơn giản để sắp xếp các nước đi
        score = 0
        # Check if a piece was captured and it's a string before accessing its type
        # Simplified the check slightly, as move.piece_captured will be None or a string from Board.move
        if isinstance(move.piece_captured, str) and len(move.piece_captured) > 1 and move.piece_captured != '--':
            # Ưu tiên ăn quân có giá trị cao - ĐÃ TĂNG ĐIỂM THƯỞNG CHO VIỆC ĂN QUÂN
            score += PIECE_VALUES.get(move.piece_captured[1], 0) * 1.5 # Tăng điểm thưởng

        # Ưu tiên di chuyển vào trung tâm
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if move.end in center_squares:
            score += 20

        return score

    def minimax(self, board, depth, is_maximizing, alpha, beta):
        if depth == 0 or board.is_checkmate('w') or board.is_checkmate('b') or board.is_stalemate('w') or board.is_stalemate('b'):
            return board.evaluate()

        if is_maximizing:  # Lượt AI (tối đa hóa)
            max_eval = -math.inf
            # Ensure valid moves list is not empty before iterating
            valid_moves = board.get_valid_moves(self.ai_color)
            if not valid_moves:
                 return board.evaluate() # Return current evaluation if no valid moves

            for move in valid_moves:
                temp_board = deepcopy(board)
                temp_board.move(move)
                eval = self.minimax(temp_board, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, max_eval) # Corrected alpha update
                if beta <= alpha:
                    break
            return max_eval
        else:  # Lượt người chơi (tối thiểu hóa)
            min_eval = math.inf
            # Ensure valid moves list is not empty before iterating
            valid_moves = board.get_valid_moves(self.human_color)
            if not valid_moves:
                 return board.evaluate() # Return current evaluation if no valid moves

            for move in valid_moves:
                temp_board = deepcopy(board)
                temp_board.move(move)
                eval = self.minimax(temp_board, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval) # Corrected beta update
                if beta <= alpha:
                    break
            return min_eval

    def check_game_over(self):
         if self.board.is_checkmate(self.turn):
            self.game_over = True
            winner_color = "Máy" if self.turn == self.human_color else "Người"
            # This message contains Vietnamese characters
            self.game_result_message = f"Chiếu bí! {winner_color} thắng!"
         elif self.board.is_stalemate(self.turn):
            self.game_over = True
            # This message contains Vietnamese characters
            self.game_result_message = "Hòa cờ!"

    def draw_game_over_screen(self):
        screen.fill(BLACK) # Black background for game over screen

        # Display the result message
        result_text = large_font.render(self.game_result_message, True, WHITE)
        result_rect = result_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(result_text, result_rect)

        # Draw a button to return to the menu
        mouse_pos = pygame.mouse.get_pos()
        self.return_button_rect = draw_button("Return to Menu", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, mouse_pos)

# Function to draw buttons (from giaodien2 (2).py, adapted)
def draw_button(text, x, y, w, h, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    color = HOVER_COLOR if rect.collidepoint(mouse_pos) else GRAY
    pygame.draw.rect(screen, color, rect, border_radius=10)
    label = font.render(text, True, WHITE)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))
    return rect

# Game mode selection menu (from giaodien2 (2).py, adapted)
def play_mode_menu():
    while True:
        screen.fill(BROWN)
        mouse_pos = pygame.mouse.get_pos()
        a = draw_button("Play with Human", 180, 150, 280, 60, mouse_pos)
        b = draw_button("Play with AI", 180, 250, 280, 60, mouse_pos)
        return_button = draw_button("Return", 180, 350, 280, 60, mouse_pos)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if a.collidepoint(mouse_pos):
                    game = HumanVsHumanGame()
                    game.run()
                    # After game.run() finishes, return to this loop to show the menu
                elif b.collidepoint(mouse_pos):
                    game = HumanVsAIGame()
                    game.run()
                    # After game.run() finishes, return to this loop to show the menu
                elif return_button.collidepoint(mouse_pos):
                    return # Return to main menu
        pygame.display.update()

# Main menu (from giaodien2 (2).py, adapted)
def main_menu():
    while True:
        screen.fill(BROWN)
        mouse_pos = pygame.mouse.get_pos()
        play_button = draw_button("Play", 200, 200, 200, 50, mouse_pos)
        quit_button = draw_button("Quit", 200, 300, 200, 50, mouse_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(mouse_pos):
                    play_mode_menu()
                if quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

if __name__ == '__main__':
    main_menu()
    def check_game_over(self):
    # Kiểm tra cho cả hai màu
        if self.board.is_checkmate('w'):
            self.game_over = True
            self.message = "Đen chiếu hết! Trắng thua!"
        elif self.board.is_checkmate('b'):
            self.game_over = True
            self.message = "Trắng chiếu hết! Đen thua!"
        elif self.board.is_stalemate(self.turn):
            self.game_over = True
            self.message = "Hòa cờ do hết nước đi!"