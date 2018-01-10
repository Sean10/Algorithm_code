class Solution {
public:
    int titleToNumber(string s) {
        int pow = 1;
        int ans = 0;
        do{
            ans *= 26;
            int temp = s.front()-'A'+1;
            ans += temp;
            s.erase(s.begin());
        }while(!s.empty());
        return ans;
    }
};
