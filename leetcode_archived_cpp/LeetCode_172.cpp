class Solution {
public:
    int trailingZeroes(int n) {
        int cnt = 0;
        for(long long i = 5;n/i > 0; i *= 5)
        {
            cnt += n/i;
        }
        return cnt;
    }
};
