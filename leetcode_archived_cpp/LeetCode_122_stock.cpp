class Solution {
public:
    int maxProfit(vector<int>& prices) {
        if(prices.size() <= 1)
            return 0;
        int ans = 0;
        for(int i = 1;i < prices.size();i++)
            ans += prices[i] - prices[i-1] > 0 ? prices[i]-prices[i-1]:0;
        return ans;
    }
};
// Solution 2
// class Solution {
// public:
//     int maxProfit(vector<int>& prices) {
//         if(prices.size() <= 1)
//             return 0;
//         int ans = 0;
//         int valley = prices[0];
//         int peak = prices[0];
//
//         int i = 0;
//         int len = prices.size();
//         while (i < len-1)
//         {
//             while (i < len-1 && prices[i] >= prices[i+1])
//                 i++;
//             valley = prices[i];
//             while(i < len-1 && prices[i] <= prices[i+1])
//                 i++;
//             peak = prices[i];
//             ans += peak - valley;
//         }
//         return ans;
//     }
// };
