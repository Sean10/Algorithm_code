class Solution:
    def summaryRanges(self, nums: List[int]) -> List[str]:
        if not nums:
            return []
        res = []
        last = None
        begin = None
        for i in nums:
            if None == last:
                last = i
                begin = i
                continue
            
            if i != last + 1 and last != begin:
                temp = f"{begin}->{last}"
                res.append(temp)
                begin = i
            elif i != last + 1 and last == begin:
                temp = f"{last}"
                begin = i
                res.append(temp)

            last = i
        if begin != last:
            res.append(f"{begin}->{last}")
        else:
            res.append(f"{begin}")
        return res

            
