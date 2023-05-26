class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        fill(remove(nums.begin(),nums.end(),0),nums.end(),0);
    }
};

class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        int j = 0;
        int len = nums.size();
        for(int i = 0;i < len;i++)
            if(nums[i] != 0)
            {
                nums[j++] = nums[i];
            }

        while(j < len)
            nums[j++] = 0;
    }
};
