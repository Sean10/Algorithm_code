class Solution {
public:
    int arrayPairSum(vector<int>& nums) {
        std::stable_sort(nums.begin(), nums.end());
        int sum = 0;
        bool tmp = true;
        vector<int>::iterator i;
        for(i = nums.begin(); i != nums.end(); i++)
        {
            if(tmp)
                sum += *i;
            tmp = !tmp;
        }
        return sum;
    }
};
