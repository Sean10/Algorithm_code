// DP
class Solution {
public:
    int maxProfit(vector<int>& prices, int fee) {
        int hold = 0 - prices[0], sold = 0;

        for (auto i: prices)
        {
            hold = max(hold, sold - i);
            sold = max(sold, hold + i - fee);
        }
        return sold;
    }
};
