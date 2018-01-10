class Solution {
public:
    bool judgeCircle(string moves) {
        int vertical = 0,horizon = 0;
        for(int i = 0;i < moves.size(); i++)
        {
            switch(moves[i])
            {
                case 'U':
                    vertical++;
                    break;
                case 'D':
                    vertical--;
                    break;
                case 'L':
                    horizon++;
                    break;
                case 'R':
                    horizon--;
                    break;
                default:
                    break;
            }
        }
        if(vertical == 0 && horizon == 0)
            return true;
        else
            return false;
    }
};
