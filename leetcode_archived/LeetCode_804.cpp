class Solution {
public:
    int uniqueMorseRepresentations(vector<string>& words) {
        vector<string> code={".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."};
        
        int ans = 0;
        unordered_map<string, int> ss;
        for (auto i: words)
        {
            string temp = "";
            for (auto j: i)
            {
                temp += code[j-a];
            }
            if (!ss.count(temp))
            {
                ss[temp]++;
                ans ++;
            }
            
        }
        return ans;
        
    }
};
