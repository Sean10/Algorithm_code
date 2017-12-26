class Solution {
public:
    bool checkRecord(string s) {
        int cnt_L = 0, cnt_A = 0;
        for(int i = 0;i < s.size(); i++)
        {
            switch(s[i])
            {
                case 'L':
                    cnt_L++;
                    break;
                case 'A':
                    cnt_A++;
                default:
                    cnt_L = 0;
                    break;
            }

            if(cnt_L > 2 || cnt_A > 1)
                return false;
        }
        return true;
    }
};
