class Solution {
public:
    string intToRoman(int num) {
        vector<vector<string>> k =  {{"", "M", "MM", "MMM"},
                                     {"", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"},
                                     {"", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"},
                                     {"", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"}};
        return k[0][num/1000] + k[1][num%1000/100] + k[2][num%100/10] + k[3][num%10];

    }
};
