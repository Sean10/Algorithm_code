class Solution {
public:
    int arrangeCoins(int n) {
        return floor(-0.5+sqrt(0.25+2*(long long)n));
    }
};
