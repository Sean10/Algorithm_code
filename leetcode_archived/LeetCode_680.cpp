class Solution {
public:
    bool validPalindrome(string s) {
        return valid(s, 0 ,s.size()-1, 1);
    }

    bool valid(string s, int left, int right, int num)
    {
        while(left < right)
        {
            if(s[left] == s[right])
            {
                left++;
                right--;
            }else
                return num > 0&& ( valid(s,left,right-1,num-1) || valid(s,left+1,right,num-1));
        }
        return true;
    }
};


// TLE
class Solution {
public:
    bool validPalindrome(string s) {
        return valid(s,0,s.size()-1,1);
    }

    bool valid(string s, int left, int right, int num)
    {
        if(left >= right)
            return true;
        if(s[left] == s[right])
            return valid(s,left+1,right-1,num);
        else
            return num > 0 && (valid(s,left+1,right,num-1) || valid(s,left,right-1,num-1));
    }
};
