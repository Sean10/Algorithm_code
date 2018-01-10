class Solution {
public:
    int findMaxConsecutiveOnes(vector<int>& nums) {
        int max_length = 0;
        int curr_length = 0;
        vector<int>::iterator it;
        for(it = nums.begin(); it != nums.end(); it++)
        {
            if(*it == 1)
            {
                curr_length++;
            }else{
                curr_length = 0;
            }

            if (curr_length > max_length)
                max_length = curr_length;
        }
        return max_length;
    }
};
