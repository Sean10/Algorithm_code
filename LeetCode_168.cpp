class Solution {
public:
    string convertToTitle(int n) {
        string ans;
        char c;
        do{
            n -=1;
            c = 'A'+n%26;
            ans = c + ans;
            n/=26;

        }while(n);
        return ans;
    }
};
