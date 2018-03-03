class Solution {
public:
    bool validUtf8(vector<int>& data) {
        int state = 0;
        for (int i: data)
        {
            if (state == 0)
            {
                if (i >> 3 == 0b11110) state = 3;
                else if (i >> 4 == 0b1110) state = 2;
                else if (i >> 5 == 0b110) state = 1;
                else if (i >> 7 == 0b0) state = 0;
                else return false;
            }
            else
            {
                if (i >> 6 != 0b10)
                    return false;
                state--;
            }
        }
        return state == 0;
    }
};
