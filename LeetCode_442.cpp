// class Solution {
// public:
//     vector<int> findDuplicates(vector<int>& nums) {
//         vector<int> ans;
//         set<int> tmp;
//
//         for(int i = 0;i < nums.size();i++)
//         {
//             if(tmp.find(nums[i]) == tmp.end())
//                 tmp.insert(nums[i]);
//             else
//                 ans.push_back(nums[i]);
//         }
//         return ans;
//     }
// };


class Solution {
public:
    vector<int> findDuplicates(vector<int>& nums) {
        vector<int> ans;

        for(int i = 0;i < nums.size();i++)
        {
            nums[abs(nums[i])-1] = -nums[abs(nums[i])-1];
            if(nums[abs(nums[i])-1] > 0)
                ans.push_back(abs(nums[i]));
        }
        return ans;
    }
};
