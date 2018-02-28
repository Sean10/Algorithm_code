class Solution {
public:
    bool hasAlternatingBits(int n) {
        int d = n&1;
        while (d == (n&1))
        {
            d = 1-d;
            n >>= 1;
        }
        return n == 0;
    }
};
