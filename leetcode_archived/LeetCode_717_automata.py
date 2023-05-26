class Solution:
    def isOneBitCharacter(self, bits):
        """
        :type bits: List[int]
        :rtype: bool
        """
        flag = 0
        for i in bits:
            if flag == 1:
                flag = 2
            elif flag == 2 and i == 0:
                flag = 0
            elif i == 1:
                flag = 1

        if flag == 2:
            return False
        else:
            return True
        
