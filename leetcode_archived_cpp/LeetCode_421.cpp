class Solution {
public:
    int findMaximumXOR(vector<int>& nums) {
        int max_result = 0, left_of_num = 0;

        for (int i = 31;i >= 0; i--)
        {
            left_of_num |= 1 << i;
            unordered_set<int> set_;
            for (int num: nums)
                set_.insert(left_of_num & num);

            int greedy_try = max_result | (1 << i);
            for (int temp: set_)
            {
                int another = temp ^ greedy_try;
                if (set_.find(another) != set_.end())
                {
                    max_result = greedy_try;
                    break;
                }
            }
        }
        return max_result;
    }
};
