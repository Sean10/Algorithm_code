/*
leetCode 1
这道题只要求返回2个值的结果即可，如果衍生出去，返回所有能得到结果的值对，就可以用回溯法了应该。

如果考虑所有测试样例的话，可能有以下几种边界情况吧。
1. 样例中可能有多个可能解（不过姑且按照这道题设，应该不会有)
2. 如果没有结果的话?
3. 如果输入的列表不是有序列表?
	将其排序一下，再进行二分查找，恐怕可以将时间复杂度从O(n^2)降到O(logn)
    看了下参考答案，原来用hash table直接就能到O(n),太棒了。

4. 对复数、大数的考虑？
 */


#include <iostream>
#include <map>
#include <vector>

using namespace std;



class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        map <int, int> list;
        map <int, int>::iterator iter;
        vector<int> ans(2, 0);
        for(int i = 0;i < nums.size();i++)
        {
            list.insert(pair<int,int>(nums[i],i));
        }

        for(int i = 0;i < nums.size();i++)
        {
            int complement = target - nums[i];
            iter = list.find(complement);
            if(iter != list.end() && iter->second != i)
            {
                ans[0] = i;
                ans[1] = iter->second;
                return ans;
            }
        }
    }
};

int main(void)
{
	Solution sol;


	int tmp[] = { 2,7,11,15};
    vector<int> nums(begin(tmp), end(tmp));


	int target = 9;

	vector<int> ans(2,-1);

	ans = sol.twoSum(nums,target);

	for(int i = 0; i < 2; i++)
	{
		cout << ans[i] << endl;
	}
}
