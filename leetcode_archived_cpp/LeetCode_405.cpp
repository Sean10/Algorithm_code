class Solution {
public:
    string toHex(int num) {
        if (num == 0)
            return "0";
        string alpha="0123456789abcdef";
        unsigned int num_ = num;
        // cout << (temp^(1 << 32) ) << endl;
        // num = num > 0 ? num : temp^(1 << 32);
        // cout << temp;
        string ans;
        while(num_)
        {
            ans = alpha[num_ & 15] + ans;
            num_ >>= 4;
        }
        return ans;
    }
};


class Solution {
public:
    string toHex(int num) {
        if (num == 0)
            return "0";
        string alpha="0123456789abcdef";
        // unsigned int num_ = num;
        // cout << (temp^(1 << 32) ) << endl;
        num = num > 0 ? num : num^(1 << 32);
        // cout << temp;
        string ans;
        int cnt = 0;
        while(num && cnt++ < 8)
        {
            ans = alpha[num & 15] + ans;
            num >>= 4;
            // cout << num << endl;
        }
        return ans;
    }
};
