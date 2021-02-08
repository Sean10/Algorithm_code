class Solution {
public:
    bool rotateString(string A, string B) {
        return A.size() != B.size() ? false : (A+A).find(B) != string::npos;

    }
};
