class Solution {
public:
    bool isValid(string s) {
        stack<char> flag;
        map<char,char> ch = {{'(',')'},{'[',']'},{'{','}'}};
        for(int i = 0;i < s.size(); i++)
        {
            if(s[i] == '(' || s[i] == '[' || s[i] == '{')
                flag.push(s[i]);
            else if(s[i] == ')' || s[i] == ']' || s[i] == '}')
            {
                if(flag.empty())
                    return false;
                char temp = flag.top();
                flag.pop();
                if(ch[temp] != s[i])
                    return false;
            }
        }
        if(flag.empty())
            return true;
        return false;
    }
};
