class Solution {
public:
    void wiggleSort(vector<int>& nums) {
        vector<int> s(nums);
        sort(s.begin(), s.end());
        for(int i = 0, j = (nums.size()+1)/2, k = nums.size()-1;k >= 0;k--)
        {
            nums[k] = s[k&1 ? j++ : i++];
        }
    }
};
