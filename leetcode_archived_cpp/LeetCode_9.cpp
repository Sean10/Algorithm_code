class Solution {
public:
    bool isPalindrome(int x) {
        if(x < 0)
            return false;
        int i = x, rev = 0;
        while(i > 0)
        {
            rev = rev*10 + i%10;
            i /= 10;
        }
        cout << rev << ' ' << x;
        return rev == x;
    }
};
