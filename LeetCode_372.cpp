class Solution {
public:
    int superPow(int a, vector<int>& b) {
        if(b.empty()) return 1;
        int last_digit = b.back();
        b.pop_back();
        return powmod(superPow(a,b), 10) * powmod(a, last_digit)%base;
    }

private:
    const int base = 1337;
    int powmod(int a, int b)
    {
        a %= base;
        int ans = 1;
        for(int i = 0;i < b; i++)
            ans = (ans * a) % base;
        return ans;
    }
};
