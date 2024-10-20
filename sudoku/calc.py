from typing import List, Tuple, Set
from image_processor import process_sudoku_image

def solve_sudoku(board: List[List[int]]) -> bool:
    candidates = initialize_candidates(board)
    if not (simple_solve(board, candidates) or advanced_solve(board, candidates)):
        return False
    return backtrack_solve(board, candidates)

def initialize_candidates(board: List[List[int]]) -> List[List[Set[int]]]:
    candidates = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                candidates[i][j] = set()
                update_candidates(board, candidates, i, j, board[i][j])
    return candidates

def update_candidates(board: List[List[int]], candidates: List[List[Set[int]]], row: int, col: int, num: int) -> None:
    for i in range(9):
        candidates[row][i].discard(num)
        candidates[i][col].discard(num)
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            candidates[i][j].discard(num)

def simple_solve(board: List[List[int]], candidates: List[List[Set[int]]]) -> bool:
    changed = True
    while changed:
        changed = False
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0 and len(candidates[i][j]) == 1:
                    num = candidates[i][j].pop()
                    board[i][j] = num
                    update_candidates(board, candidates, i, j, num)
                    changed = True
    return all(all(cell != 0 for cell in row) for row in board)

def advanced_solve(board: List[List[int]], candidates: List[List[Set[int]]]) -> bool:
    changed = True
    while changed:
        changed = False
        if xy_wing(board, candidates):
            changed = True
    return all(all(cell != 0 for cell in row) for row in board)

def xy_wing(board: List[List[int]], candidates: List[List[Set[int]]]) -> bool:
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0 and len(candidates[i][j]) == 2:
                xy = candidates[i][j]
                for k in range(9):
                    if k != j and board[i][k] == 0 and len(candidates[i][k]) == 2:
                        yz = candidates[i][k]
                        if len(xy & yz) == 1:
                            z = (xy | yz) - (xy & yz)
                            for m in range(9):
                                if m != i and board[m][j] == 0 and len(candidates[m][j]) == 2:
                                    xz = candidates[m][j]
                                    if xz == (xy - yz) | z:
                                        # XY-Wing found
                                        eliminate = z.pop()
                                        for n in range(9):
                                            if n != i and n != m and board[n][k] == 0:
                                                if eliminate in candidates[n][k]:
                                                    candidates[n][k].remove(eliminate)
                                                    return True
    return False

def backtrack_solve(board: List[List[int]], candidates: List[List[Set[int]]]) -> bool:
    if all(all(cell != 0 for cell in row) for row in board):
        return True
    
    row, col = find_empty(board)
    for num in candidates[row][col]:
        if is_valid(board, num, (row, col)):
            board[row][col] = num
            old_candidates = [row[:] for row in candidates]
            update_candidates(board, candidates, row, col, num)
            
            if backtrack_solve(board, candidates):
                return True
            
            board[row][col] = 0
            candidates = old_candidates
    
    return False

def find_empty(board: List[List[int]]) -> Tuple[int, int]:
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def is_valid(board: List[List[int]], num: int, pos: Tuple[int, int]) -> bool:
    for j in range(len(board[0])):
        if board[pos[0]][j] == num and pos[1] != j:
            return False
    
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False
    
    box_x, box_y = pos[1] // 3, pos[0] // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False
    
    return True

def print_board(board: List[List[int]]) -> None:
    for i in range(len(board)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - -")
        for j in range(len(board[0])):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            if j == 8:
                print(board[i][j])
            else:
                print(str(board[i][j]) + " ", end="")

def solve_sudoku_from_image(image_path: str) -> List[List[int]]:
    # 从图像中提取数独问题
    board = process_sudoku_image(image_path)
    
    print("从图像中识别的数独问题：")
    print_board(board)
    
    # 解决数独问题
    if solve_sudoku(board):
        print("\n解决方案：")
        print_board(board)
        return board
    else:
        print("无法解决此数独问题")
        return None

# 示例使用
if __name__ == "__main__":
    # 从图像解析并解决数独
    image_path = "image/Screenshot 2024-10-20 at 15.58.49.png"  # 替换为实际的图像路径
    solved_board = solve_sudoku_from_image(image_path)
    
    # 如果需要，您还可以保留之前的示例
    # board = [
    #     [5, 3, 0, 0, 7, 0, 0, 0, 0],
    #     ...
    # ]
    # print("数独问题：")
    # print_board(board)
    # solve_sudoku(board)
    # print("\n解决方案：")
    # print_board(board)
