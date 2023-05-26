class Solution {
public:
    int hammingDistance(int x, int y) {
        int temp = x ^ y;
        int cnt = 0;
        for(;temp;cnt++)
        {
            temp &= temp-1;
        }
        return cnt;
    }
};
