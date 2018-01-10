class Solution {
public:
    int distributeCandies(vector<int>& candies) {
        set<int> temp;
        for(int i = 0;i < candies.size(); i++)
            temp.insert(candies[i]);
        return min(candies.size()/2, temp.size());
    }
};
