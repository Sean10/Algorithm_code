// 失败的代码，尝试用自动机，但是没能成功
class Solution {
public:
    string pushDominoes(string dominoes) {
        int state = 0;
        for (int i = 0; i < dominoes.size(); i++)
        {
            if (state == 0)
            {
                if (i == 'L')
                {
                    state = 1;
                    int j = i;
                    for (; j > 0 && dominoes[j] == '.' && dominoes[j-1] != 'R'; j--)
                        dominoes[j] = 'L';
                    if(j == 0 && dominoes[j] ==  '.' )
                        dominoes[0] = 'L';
                }
                else {
                    state = 2;
                }
            }
            else if (state == 1)
            {
                if (dominoes[i] == 'R' )
                {
                    state = 2;
                }else if (dominoes[i] == '.')
                {
                    state = 0;
                }
            }
            else 
            {
                if (dominoes[i] == '.')
                    dominoes[i] = 'R';  
                else if (dominoes[i] == 'L')
                    state = 0;
            }
        }
        return dominoes;
    }
};

class Solution {
public:
    string pushDominoes(string dominoes) {
        string ans = "";
        dominoes = "L" + dominoes + "R";
        for (int i = 0, j = 1; j < dominoes.size(); j++)
        {
            if (dominoes[j] == '.') continue;
            if (i > 0)
                ans += dominoes[i];
            if (dominoes[i] ==  dominoes[j] )
                ans += string(j-i-1, dominoes[i]);
            else if (dominoes[i] == 'R' && dominoes[j] == 'L')
                ans += string((j-i-1)/2, 'R') + string((j-i-1)%2, '.') + string((j-i-1)/2, 'L');
            else 
                ans += string(j-i-1, '.');
            i = j;
        }
        return ans;
    }
};