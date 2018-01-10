/*
leetCode 1
这道题只要求返回2个值的结果即可，如果衍生出去，返回所有能得到结果的值对，就可以用回溯法了应该。

如果考虑所有测试样例的话，可能有以下几种边界情况吧。
1. 样例中可能有多个可能解（不过姑且按照这道题设，应该不会有)
2. 如果没有结果的话?
3. 如果输入的列表不是有序列表?
	将其排序一下，再进行二分查找，恐怕可以将时间复杂度从O(n)降到O(logn)
4. 对复数、大数的考虑？
 */


#include <iostream>
#include <vector>

#ifdef _DEBUG
#define DEBUG std::cout<<__LINE__;
#else
#define DEBUG
#endif

using namespace std;



class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        vector<int> ans(2);

		bool flag = false;
        for(int i = 0; i < nums.size();i++)
        {
			//cout << "error" <<endl;
			//DEBUG;

			// ans.push_back(i);
			ans[0] = i;
			for(int j = i+1; j < nums.size();j++)
			{
				if(nums[j] == target-nums[i])
				{
					//ans.push_back(j);
					ans[1] = j;
					flag = true;
					//DEBUG;
                    //cout << j << "hll" << endl;
					//cout << "Succeed" <<endl;
					return ans;
				}
			}

			if(!flag)
			{
				//flag = false;
				ans[0] = 0;
			}
        }
    }
};


int main(void)
{
	Solution sol;


	int tmp[] = { 2,7,11,15};
    vector<int> nums(begin(tmp), end(tmp));
	// nums.push_back(2);
    //
	// nums.push_back(7);
	// nums.push_back(11);
	// nums.push_back(15);

	int target = 9;

	vector<int> ans(2,-1);

	ans = sol.twoSum(nums,target);

	for(int i = 0; i < 2; i++)
	{
		cout << ans[i] << endl;
	}
}
