class Solution {
public:
    vector<int> selfDividingNumbers(int left, int right) {
        vector<int> ans;
        for (int i = left; i <= right; i++)
        {
            int j = -1;
            for (j = i; j > 0;)
            {
                if (j%10 == 0 || i%(j%10) != 0)
                    break;
                j /= 10;
            }
            if (j == 0)
                ans.push_back(i);
            
        }
        return ans;
    }
};
