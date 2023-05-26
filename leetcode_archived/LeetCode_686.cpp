class Solution {
public:
    int repeatedStringMatch(string A, string B) {
        int cnt = 1;
        string temp = A;
        for(;A.find(B) == string::npos && A.size() <= 10000;cnt++)
            A.append(temp);
        //cout << A;
        if(A.size() > 10000)
            return -1;
        return cnt;
    }
};
