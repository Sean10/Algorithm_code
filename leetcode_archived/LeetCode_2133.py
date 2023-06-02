class Solution:
    def checkValid(self, matrix: List[List[int]]) -> bool:
        n = len(matrix)
        occur = set()
        for i in range(n):
            occur.clear()
            for j in range(n):
                if matrix[i][j] not in occur:
                    occur.add(matrix[i][j])
                else:
                    return False
        
        for i in range(n):
            occur.clear()
            for j in range(n):
                if matrix[j][i] not in occur:
                    occur.add(matrix[j][i])
                else:
                    return False
        return True
