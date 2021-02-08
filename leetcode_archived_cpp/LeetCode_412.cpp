class Solution {
public:
    vector<string> fizzBuzz(int n) {
        string a = "Fizz", b = "Buzz";
        vector<string> ans;
        for(int i = 1;i <= n;i++)
        {
            if(i % 3 != 0 && i % 5 != 0)
                ans.push_back(to_string(i));
            else if(i % 3 == 0 && i % 5 == 0)
                ans.push_back(a+b);
            else if(i % 3 == 0)
                ans.push_back(a);
            else
                ans.push_back(b);


        }
        return ans;
    }
};
