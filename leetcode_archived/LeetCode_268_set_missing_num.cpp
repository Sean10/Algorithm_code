// class Solution {
// public:
//     int missingNumber(vector<int>& nums) {
//         set<int> set_;
//         int len = nums.size();
//         for(int i = 0;i < len;i++)
//         {
//             set_.insert(nums[i]);
//         }
//
//         for(int i = 0;i < len+1;i++)
//         {
//             if(set_.find(i) == set_.end())
//                 return i;
//         }
//     }
// };

class Solution {
public:
    int missingNumber(vector<int>& nums) {
        int len = nums.size();

        int result = nums.size();
        int i = 0;
        for(auto num:nums)
        {
            result ^= i;
            result ^= num;
            i++;
        }
        return result;
    }
};
