# -*- coding: UTF-8 -*-

class Solution:
    def twoSum(self, nums, target):
        dict ={};
        for i,x in enumerate(nums):
            dict.setdefault(x,i);

        for i,x in enumerate(nums):
            complement = target - x;
            if(dict.__contains__(complement) and dict.get(complement) != i):
                pos = dict.get(complement);
                return [i, pos];

t = Solution()
mylist = [2,7,9,11];
ans = t.twoSum(mylist, 9);
print(ans);
#print mylist[1:];
