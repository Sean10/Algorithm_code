class Solution {
public:
    bool isOneBitCharacter(vector<int>& bits) {
        int flag = 0;
        vector<int>::iterator it;
        for(it = bits.begin(); it != bits.end(); it++)
        {
            if(flag == 1)
            {
                flag = 2;
            }else if(flag == 2 && *it == 0)
            {
                flag = 0;
            }else if(*it == 1)
            {
                flag = 1;
            }
        }

        if(flag == 2)
            return false;
        else if (flag == 0)
            return true;
    }
};
