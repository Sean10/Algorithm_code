# 似乎适合双链法?
# 边界场景跟sum(count) >= 1可知不会遇到

from collections import Counter
class Solution:
    def sampleStats(self, count: List[int]) -> List[float]:
        sum_res = 0
        count_res = sum(count)
        for i,v in enumerate(count):
            sum_res += i*v
        mean = sum_res / count_res
        
        temp_order_sum = 0
        mean_sum = 0
        if count_res % 2 == 0:
            flag = 0
            for i,v in enumerate(count):
                if v <= 0:
                    continue
                temp_order_sum += v

                if temp_order_sum >= count_res // 2 + 1:
                    # print(i, v, mean_sum, temp_order_sum)
                    mean_sum += i
                    if flag == 0:
                        mean_sum += i
                    break
                elif temp_order_sum >= count_res // 2:
                    # print(i, v, mean_sum, temp_order_sum)
                    mean_sum += i
                    flag = 1

            median = mean_sum / 2
        else:
            for i,v in enumerate(count):
                temp_order_sum += v
                if temp_order_sum >= count_res // 2 + 1:
                    median = i
                    break

    
        minimum = 0
        for i, v in enumerate(count):
            if v > 0:
                minimum = i
                break
        maximum = 0
        for i, v in enumerate(reversed(count)):
            if v > 0:
                maximum = 255 - i
                break
        count_most_common = 0
        for i, v in enumerate(count):
            if v > 0 and v > count_most_common:
                count_most_common = v
                count_most_common_index = i
        return [minimum, maximum, mean, median, count_most_common_index]


        
