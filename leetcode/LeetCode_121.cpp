class Solution {
public:
    int maxProfit(vector<int>& prices) {

        int max_profit = 0;
        int min = INT_MAX;
        for(int i = 0;i < prices.size();i++)
        {
            if(min > prices[i])
                min = prices[i];
            max_profit = max(max_profit, prices[i] - min);
        }
        return max_profit;
    }
};
