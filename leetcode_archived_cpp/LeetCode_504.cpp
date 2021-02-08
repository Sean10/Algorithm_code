class Solution {
public:
    string convertToBase7(int num) {
        int x = abs(num);
        string ans;
        do
        {
            ans = to_string(x%7) + ans;
        }while(x/=7);
        return (num>=0?"":"-")+ans;
    }
};
