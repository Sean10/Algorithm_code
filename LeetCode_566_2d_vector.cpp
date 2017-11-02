class Solution {
public:
    vector<vector<int>> matrixReshape(vector<vector<int>>& nums, int r, int c) {
        if(nums[0].size()*nums.size() != r*c)
            return nums;

        vector<vector<int>> tmp(r);
        for(int i = 0;i < tmp.size(); i++)
        {
            tmp[i].resize(c);
        }

        int it_pos = 0;
        vector<vector<int>>::iterator it_x = nums.begin();
        vector<int>::iterator it = nums[it_pos].begin();

        for(int i = 0;i < r;i++)
            for(int j = 0; j < c;j++)
            {
                tmp[i][j] = *it;
                it++;
                if(it == nums[it_pos].end())
                {
                    it_pos++;
                    it = nums[it_pos].begin();
                }

            }
        return tmp;
    }
};
