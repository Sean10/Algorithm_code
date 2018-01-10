class Solution {
public:
    bool isHappy(int n) {
        vector<int> circle;
        while(n != 1 && find(circle.begin(), circle.end(), n) == circle.end())
        {
            circle.push_back(n);
            n = getSquareNum(n);
        }
        if( n == 1)
            return true;
        return false;
    }

    int getSquareNum(int n)
    {
        int ans = 0;
        while(n)
        {
            int temp = n%10;
            n /= 10;
            ans += temp*temp;
        }
        return ans;
    }

};
