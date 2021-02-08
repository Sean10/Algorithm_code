class Solution:
    def twoSum(self, numbers, target):
        """
        :type numbers: List[int]
        :type target: int
        :rtype: List[int]
        """
        dict ={};
        for i,x in enumerate(numbers):
            dict.setdefault(x,i);

        for i,x in enumerate(numbers):
            complement = target - x;
            if(dict.__contains__(complement) and dict.get(complement) != i):
                pos = dict.get(complement);
                ans = [i+1,pos+1]
                ans.sort()
                return ans;
