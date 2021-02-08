class Solution {
public:
    int nextGreaterElement(int n) {
        auto digits = to_string(n);
        next_permutation(digits.begin(), digits.end());
        int ans = stol(digits);
        return (ans > INT_MAX || ans <= n) ? -1 : ans;
    }
};
