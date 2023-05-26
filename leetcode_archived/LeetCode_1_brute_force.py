# -*- coding: UTF-8 -*-

class Solution:
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        ans = [0,0];
        flag = 0;
        for i, x in enumerate(nums):
            ans[0] = i;
            #print "x:",i, x;

            for j,y in enumerate(nums[i+1:]):
                #print "y:", j,y;

                if(y == target-x):
                    ans[1] = j+i+1;
                    flag = 1;
                    #print "y:", j,y;
                    return ans;

            if(flag == 0):
                ans[0] = 0;

t = Solution()
mylist = [3,2,4];
ans = t.twoSum(mylist, 6);
print ans;
#print mylist[1:];
